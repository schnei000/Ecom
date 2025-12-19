const ProductCard = ({ product }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden group transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <img
        src={product.image}
        alt={product.nom}
        className="w-full h-64 object-cover transition-transform duration-300 group-hover:scale-105"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2 truncate">
          {product.nom}
        </h3>
        <p className="text-xl font-bold text-gray-900 mb-4">
          {product.prix.toFixed(2)} €
        </p>
        <button className="w-full bg-black text-white py-2 rounded-md hover:bg-gray-800 transition-colors duration-300 transform group-hover:bg-blue-600">
          Ajouter au panier
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
