from typing import Optional, List, Union

from _io import BufferedReader

from models import objects, Video


async def get_videos(video_language: str) \
        -> List[List[Optional[List[Union[int, str, BufferedReader]]]]]:
    videos = await objects.execute(Video.select().where(Video.language == video_language))
    video_ids = []
    video_ios = []

    for video in videos:
        if video.video_id:
            video_ids.append([video.id, video.video_id])
        else:
            video_io = open(video.video_path, 'rb')
            video_ios.append([video.id, video_io])
    return [video_ids, video_ios]


async def save_video_id(video_model_id: int, video_id: str) -> None:
    video = await objects.get(Video, id=video_model_id)
    video.video_id = video_id
    await objects.update(video, ['video_id'])
