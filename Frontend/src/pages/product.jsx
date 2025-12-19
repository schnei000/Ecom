import {useState,useEffect} from 'react';
import ProductCard from '../components/ProductCard.jsx';
import {fetchProducts} from '../api/ProductApi.js';

function Products() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect (() => {
    const getProducts = async () => {
      try{
        const data = await fetchProducts();
        setProducts(data);

      }
      catch (err) {
        setError(err.message);
      }
      finally{
        setLoading(false);
      }
    }
    getProducts();
  },[]);
  if (loading) {
    return (
      <p className="text-center py-12 text-red-500">Chargement...</p>

    );
  }
  
  if (error) {
    return (
      <p className="text-center py-12 text-red-500">Erreur: {error}</p>
    );
  }

  return (
    <section className="py-12 px-4">
      <h2 className="text-3xl font-bold text-center mb-8">Nos Produits</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </section>
  );
}

export default Products;