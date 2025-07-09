SYNONYM_MAPPING = {
    #Synonyms for entities
    "sort_by": {
        "highest-rated": "vote_average.desc",
        "top-rated": "vote_average.desc",
        "best-rated": "vote_average.desc",
        "most popular": "popularity.desc",
        "trending": "popularity.desc",
        "latest": "release_date.desc",
        "newest": "release_date.desc",

        #Turkish equivalents
        "en yüksek puanlı": "vote_average.desc",
        "en iyi puanlı": "vote_average.desc",
        "en popüler": "popularity.desc",
        "trend": "popularity.desc",
        "son çıkan": "release_date.desc",
        "en yeni": "release_date.desc"
    },

    "runtime": {
        "short": (None, 90),  #Less than 90 minutes
        "long": (120, None),  #More than 120 minutes
        "medium": (90, 120),  #Between 90 and 120 minutes
        "quick": (None, 90),  #Synonym for short

        #Turkish equivalents
        "kısa": (None, 90),
        "uzun": (120, None),
        "orta": (90, 120),
        "hızlı": (None, 90)
    },

    "budget": {
        "low budget": 10_000_000,  #Less than $10 million
        "mid budget": (10_000_001, 99_000_000),  #Between $10 million and $99 million
        "big budget": 100_000_000,  #More than $100 million
        "indie": 10_000_000,       #Synonym for low-budget
        "blockbuster": 100_000_000, #Synonym for big-budget

        #Turkish equivalents
        "düşük bütçeli": 10_000_000,
        "orta bütçeli": (10_000_001, 99_000_000),
        "büyük bütçeli": 100_000_000,
        "bağımsız": 10_000_000,
        "gişe rekorları kıran": 100_000_000
    },

    "exclude": {
        "horror": "horror",  #User dont want horror movies
        "romance": "romance",  #User doesnt want romance movies
        "animated": "animation",  #User excludes animated movies
        
        #Turkish equivalents
        "korku": "horror",
        "romantik": "romance",
        "animasyon": "animation"
    }
}
