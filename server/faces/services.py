from ..photos.models import Photo
from .cosine_similarity import cosine_similarity
from .models import Face


def search_face(photo_obj: Photo, threshold=0.1, exclude_urls=None):
    """Search input photo against all faces in database.

    example results:

        ```
        [
            [obj, ...],  # face 1 matches
            [obj, ...],  # face 2 matches
            ...
        ]
        ```

    Args:
        photo_obj (Photo): photo to search
        threshold (float, optional): minimum score to consider a match. Defaults to 0.1.

    Returns:
        list: _description_
    """
    # calculate cosine distance to all face in database
    # TODO: use numpy vectorized operation to speed up consine distance calculation
    # TODO: Use k-NN algorithm to speed up search time

    if exclude_urls is None:
        exclude_urls = []

    faces = Face.query.all()
    results = []
    for face_to_search in photo_obj.faces:
        current_results = []
        for face in faces:
            # TODO: investigate if batch cosine similarity calculation would be faster
            score = cosine_similarity(face.encoding, face_to_search.encoding)

            if score > threshold and face.photo.url not in exclude_urls:
                current_results.append({"face": face, "score": float(score)})

        # TODO: Use faster sorting algorithm
        current_results.sort(key=lambda x: x["score"], reverse=True)
        results.append(current_results)

    return results
