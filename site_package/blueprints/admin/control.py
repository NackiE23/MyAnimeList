from typing import Optional, List

from site_package.extensions import db


class AdminModel:
    def __init__(self, model: db.Model, order=None, *, model_name=None):
        self.model_name = model_name or model.__name__
        self.model = model
        self.order = order

    def get_items(self):
        if self.order:
            return self.model.query.order_by(self.order).all()
        return self.model.query.all()


class Admin:
    def __init__(self):
        self.models = list()

    def add_model(self, model: AdminModel) -> None:
        self.models.append(model)

    def add_models(self, models: List[AdminModel]) -> None:
        self.models.extend(models)

    def get_model_by_name(self, model_name: str) -> Optional[AdminModel]:
        for model in self.models:
            if model_name.lower() == model.model_name.lower():
                return model
        return None
