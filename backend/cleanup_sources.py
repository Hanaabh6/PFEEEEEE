from backend.base import keyword_index_collection

deleted = keyword_index_collection.delete_many({
    "source": {
        "$regex": "'?(ETAGE|TD_)",
        "$options": "i"
    }
})

print("Supprimés:", deleted.deleted_count)