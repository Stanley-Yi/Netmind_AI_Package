from enum import Enum

EmbeddingTypeDict = {
    1: {"model": "text-embedding-ada-002", "dim": 1536},
}

class EmbeddingType(Enum):
    OpenAI_text_embedding_ada_002 = 1
    

    def __new__(cls, value):
        member = object.__new__(cls)
        member._value_ = value
        member.model = EmbeddingTypeDict[value]['model']
        member.dim = EmbeddingTypeDict[value]['dim']
        return member

    def __str__(self):
        return self.model




# print(EmbeddingType(1))  # 应输出: text-embedding-ada-002
# print(EmbeddingType.OpenAI_text_embedding_ada_002.dim)   # 应输出: 1536


    