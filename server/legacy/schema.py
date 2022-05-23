from ariadne import make_executable_schema, snake_case_fallback_resolvers

from .graphql import type_defs
from .core.query import query as app_query
from .core.mutation import mutation as app_mutation

queries = [app_query]
mutations = [app_mutation]

schema = make_executable_schema(
    type_defs, queries, mutations, snake_case_fallback_resolvers
)
