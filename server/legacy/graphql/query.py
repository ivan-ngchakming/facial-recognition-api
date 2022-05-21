query = """
type Query {
    photo(photoId: String!): Photo!
    photos(page: Int, profileId: String, photosPerPage: Int): PhotoPagination!
    profile(profileId: String!): Profile!
    profiles(page: Int, perPage: Int): ProfilePagination!
    identifyFace(faceId: String!): [IdentifyFaceResult]!
    task(taskCollectionId: String!): Task
    tasks: [Task]
}
"""
