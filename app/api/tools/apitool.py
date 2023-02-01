from app.models.YoutubeScrapping import Video, YoutubeChannels


def get_attr(attr_name, obj) -> str:
    if hasattr(obj, attr_name):
        return getattr(obj, attr_name)
    else:
        return "N/A"
        