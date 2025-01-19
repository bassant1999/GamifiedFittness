RUNNNING_ACTIVITY = 1

def serialize_activity(activity):
    return {
        'id': activity.id,
        'name': activity.name,
        'points': activity.points,
        'calories': activity.calories,
        'unit': {
            'id': activity.unit.id,
            'name': activity.unit.name
        }
    }
