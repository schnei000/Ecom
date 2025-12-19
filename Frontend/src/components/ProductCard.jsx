import React from 'react';

const ProductCard = ({ product }) => {
  return (
    <div className="bg-white border rounded-lg shadow-sm hover:shadow-md transition-shadow duration-300 overflow-hidden">
      <img src={product.image} alt={product.title} className="w-full h-48 object-cover" />
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{product.title}</h3>
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">{product.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold">${product.price}</span>
          <button className="bg-black text-white px-4 py-2 rounded hover:bg-gray-800 transition-colors">
            Voir Produits
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;