class ErrorAPI(Exception):
    """Error controlado que se transforma en una respuesta HTTP."""

    def __init__(self, mensaje, status_code=400):
        super().__init__(mensaje)
        self.status_code = status_code