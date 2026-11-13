"""Profile presentation data independent of GUI toolkits."""

def normalize_viewer(viewer):
    def get(key, alias=None):
        if isinstance(viewer, dict):
            return viewer.get(key, viewer.get(alias))
        return getattr(viewer, key, getattr(viewer, alias, None)) if viewer is not None else None
    return {key: get(key, alias) for key, alias in [("following", "following"), ("muted", "muted"), ("blocking", "blocking"), ("blockedBy", "blocked_by")]}

def format_profile(profile_model):
    def g(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def get_count(*keys):
        for k in keys:
            val = g(profile_model, k)
            if val is not None:
                return val
        return None

    return {
        "did": g(profile_model, "did"),
        "handle": g(profile_model, "handle"),
        "displayName": g(profile_model, "displayName") or g(profile_model, "display_name") or g(profile_model, "handle"),
        "description": g(profile_model, "description"),
        "avatar": g(profile_model, "avatar"),
        "banner": g(profile_model, "banner"),
        "followersCount": get_count("followersCount", "followers_count"),
        "followsCount": get_count("followsCount", "follows_count", "followingCount", "following_count"),
        "postsCount": get_count("postsCount", "posts_count"),
        "viewer": normalize_viewer(g(profile_model, "viewer")),
    }

