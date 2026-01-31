class BasePolicy:
    model = None

    def get_queryset(self, user):
        return self.model.objects.none()
