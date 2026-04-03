from flask import request, current_app


def get_pagination_params(default_per_page=10):
    """Extrait et normalise les paramètres de pagination depuis la requête."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', default_per_page, type=int)
    max_per_page = current_app.config.get('MAX_PER_PAGE', 100)
    page = max(1, page)
    per_page = max(1, min(per_page, max_per_page))
    return page, per_page
