from server.faces.cosine_similarity import cosine_similarity
from server.faces.models import Photo, Face


def search_face(photo_obj: Photo):
    # calculate cosine distance to all face in database
    # TODO: use numpy vectorized operation to speed up consine distance calculation
    # TODO: Use k-NN algorithm to speed up search time
    faces = Face.query.all()
    results = []
    for face_to_search in photo_obj.faces:
        current_results = []
        for face in faces:
            # TODO: investigate if batch cosine similarity calculation would be faster
            score = cosine_similarity(face.encoding, face_to_search.encoding)

            # TODO: allow configurable threshold
            if score > 0.1:
                current_results.append({"face": face, "score": float(score)})

        # TODO: Use faster sorting algorithm
        current_results.sort(key=lambda x: x["score"], reverse=True)
        results.append(current_results)

    return results
