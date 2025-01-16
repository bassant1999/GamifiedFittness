from django.core.exceptions import ObjectDoesNotExist

def get_object_or_none(model, *args, **kwargs):
    """
    A utility function to fetch a single object or return None if it doesn't exist.

    :param model: The model class to query.
    :param args: Positional arguments for query filtering (e.g., Q objects).
    :param kwargs: Keyword arguments for query filtering.
    :return: The object if found, otherwise None.
    """
    try:
        return model.objects.get(*args, **kwargs)
    except ObjectDoesNotExist:
        return None
    except model.MultipleObjectsReturned:
        return None
