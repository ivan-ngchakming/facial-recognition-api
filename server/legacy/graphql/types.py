types = """
type Profile {
    id: String!
    name: String
    facesCount: Int
    thumbnail: Face
    faces: [Face]
}

type ProfilePagination {
    pages: Int
    count: Int
    profiles: [Profile]
}

type Photo {
    id: String!
    width: Int!
    height: Int!
    array: String!
    url: String!
    faces: [Face]
}

type PhotoPagination {
    pages: Int
    count: Int
    photos: [Photo]
}

type Face {
    id: ID!
    location: [Int]
    landmarks: Landmark
    encoding: [Float]
    photo: Photo
    profile: Profile
}

type Landmark {
    chin: [[Int]]
    left_eyebrow: [[Int]]
    right_eyebrow: [[Int]]
    nose_bridge: [[Int]]
    nose_tip: [[Int]]
    left_eye: [[Int]]
    right_eye: [[Int]]
    top_lip: [[Int]]
    bottom_lip: [[Int]]
}

type IdentifyFaceResult {
    id: String
    score: Float
}

type Task {
    taskCollectionId: ID!
    status: String
    progress: Float
}
"""
