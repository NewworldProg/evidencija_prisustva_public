def ima_pravo(user, akcija, uprava=None):
    if user.is_superuser:
        return True
    if not hasattr(user, 'zaposleni'):
        return False
    if akcija == "vodja_dnevne" and user.groups.filter(name="vodja_dnevne").exists():
        return uprava and user.zaposleni.uprava == uprava
    if akcija == "admin_uprave" and user.groups.filter(name="admin_uprave").exists():
        return uprava and user.zaposleni.uprava == uprava
    return False
