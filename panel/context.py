def panel_user(request):
    return {"panel_username": request.session.get("admin_username", "")}
