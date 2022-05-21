mutation = """
type Mutation {
    photo(rbytes: String): Photo!
    deletePhoto(ids: [String]): [String]
    profile(_id: String, name: String, faceIds: [String], thumbnailId: String): Profile!
    assignFaceToProfile(faceId: String!, profileId: String!): Face!
    batchFaceRec(dirpath: String, priority: Float): Task
}
"""
