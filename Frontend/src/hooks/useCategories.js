import { useEffect, useState } from 'react';
import { fetchCategories } from '../api/ProductApi';

// Module-level cache so categories are only fetched once per session
let _cache = null;
let _promise = null;

function useCategories() {
    const [categories, setCategories] = useState(_cache ?? []);
    const [loading, setLoading] = useState(_cache === null);

    useEffect(() => {
        if (_cache !== null) {
            setCategories(_cache);
            setLoading(false);
            return;
        }

        if (!_promise) {
            _promise = fetchCategories();
        }

        _promise
            .then((data) => {
                _cache = data;
                setCategories(data);
            })
            .catch(() => {
                _promise = null; // allow retry on error
            })
            .finally(() => setLoading(false));
    }, []);

    return { categories, loading };
}

export default useCategories;
