from apps.document.utils.profile import get_documents_profile_data
from apps.fees.utils.profile import get_fee_profile_data
from apps.results.utils.profile import get_results_profile_data
from apps.plans.utils import has_feature_permission

from apps.plans.models import Feature



PROFILE_CARD_LOADERS = {
    "fees": get_fee_profile_data,
    "results": get_results_profile_data,
    "documents": get_documents_profile_data,
}

PROFILE_FEATURES = tuple(PROFILE_CARD_LOADERS.keys())


def get_card_context(user, feature_code):
    """
    Return the context for a profile card.
    """

    loader = PROFILE_CARD_LOADERS.get(feature_code)

    if loader is None:
        return {}

    return loader(user)


def get_profile_cards(user):
    """
    Return all profile cards available to the user.
    """

    cards = []

    features = (
        Feature.objects
        .filter(code__in=PROFILE_FEATURES)
        .order_by("name")
    )

    for feature in features:

        if not has_feature_permission(user, feature.code):
            continue

        context = get_card_context(user, feature.code)

        if not context:
            continue

        cards.append({
            "feature": feature,
            "template": f"accounts/profile/cards/{feature.code}.html",
            "context": context,
        })

    return cards