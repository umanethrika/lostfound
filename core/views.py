from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404

from .forms import SignUpForm, LoginForm, ItemForm
from .models import Item, Category, LOCATIONS, MatchNotification
from rapidfuzz import fuzz


# -----------------------
# Authentication Views
# -----------------------
def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = SignUpForm()
    return render(request, "core/signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect("home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = LoginForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out")
    return redirect("login")


# -----------------------
# Home & Item Handling
# -----------------------
@login_required
def home_view(request):
    """Main dashboard: upload items, see all items, filter, and check notifications."""

    # --- Handle Item Upload ---
    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user
            item.save()
            messages.success(request, f"{item.kind} item uploaded successfully!")

            # Automatic Matching (only for FOUND items)
            if item.kind == "FOUND":
                _run_auto_matching(item)

            return redirect(f"{request.path}?new_item={item.kind}")
        else:
            messages.error(request, "There was an error uploading the item.")
    else:
        form = ItemForm()

    # --- Filters for Display ---
    category_filter = request.GET.get("category")
    location_filter = request.GET.get("location")
    keyword_filter = request.GET.get("keyword")
    new_item_kind = request.GET.get("new_item")

    items = Item.objects.all().order_by("-created_at")
    if category_filter:
        items = items.filter(category_id=category_filter)
    if location_filter:
        items = items.filter(location=location_filter)
    if keyword_filter:
        items = items.filter(
            Q(title__icontains=keyword_filter) | Q(description__icontains=keyword_filter)
        )

    categories = Category.objects.all()
    user_items = Item.objects.filter(user=request.user).order_by("-created_at")

    # --- Notifications for Matches ---
    notifications = MatchNotification.objects.filter(
        lost_item__user=request.user,
        notified=False
    ).order_by("-created_at")

    context = {
        "form": form,
        "items": items,
        "categories": categories,
        "locations": LOCATIONS,
        "selected_category": category_filter,
        "selected_location": location_filter,
        "keyword": keyword_filter,
        "user_items": user_items,
        "new_item_kind": new_item_kind,
        "notifications": notifications,
    }
    return render(request, "core/home.html", context)


def _run_auto_matching(found_item):
    """Helper: try to match a FOUND item with possible LOST items."""
    lost_items = Item.objects.filter(kind="LOST")

    for lost_item in lost_items:
        # Boost if same category
        category_match = 20 if found_item.category == lost_item.category else 0

        # Fuzzy string match
        title_score = fuzz.partial_ratio(found_item.title.lower(), lost_item.title.lower())
        desc_score = fuzz.partial_ratio(found_item.description.lower(), lost_item.description.lower())

        total_score = max(title_score, desc_score) + category_match

        # Threshold: ~70 is decent, 85+ strong
        if total_score >= 70:
            MatchNotification.objects.get_or_create(
                lost_item=lost_item,
                found_item=found_item
            )


# -----------------------
# Claim Item
# -----------------------
@login_required
def claim_item(request, notif_id):
    """When a lost owner claims their item, return finder details and clean up records."""
    try:
        notif = MatchNotification.objects.get(id=notif_id, lost_item__user=request.user)
    except MatchNotification.DoesNotExist:
        raise Http404("Notification not found")

    finder_name = notif.found_item.user.name
    finder_contact = notif.found_item.contact_info

    # Delete items and notification after claim
    notif.lost_item.delete()
    notif.found_item.delete()
    notif.delete()

    return JsonResponse({
        "success": True,
        "finder_name": finder_name,
        "finder_contact": finder_contact
    })
