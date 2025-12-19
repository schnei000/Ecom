import { Link } from "react-router-dom";
import im1 from "../assets/images/im1.jpg";
import im2 from "../assets/images/im2.png";
import im3 from "../assets/images/im3.png";

function Home() {
  return (
    <section className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4">
      {/*texte*/}
      <div className="flex flex-col justify-center">
        <h2 className="text-4xl md:text-5xl font-bold leading-tight mb-4">
          Boutik Lakay <br />
          Bon Prix, Bon Kalite depuis son telePhone, Laptop ou Tablet!
        </h2>

        <p className="text-gray-600 mb-8">
          Une plateforme e-commerce fiable et conviviale qui offre une large
          gamme de produits de haute qualité à des prix compétitifs. Que vous
          soyez à la recherche des dernières tendances en matière de mode,
          d'électronique, d'articles pour la maison ou bien plus encore, Boutik
          Lakay est votre destination unique pour toutes vos envies d'achat en
          ligne.
        </p>

        <Link
          to="/products"
          className="inline-block bg-black text-white px-6 py-3 rounded-md hover:bg-gray-800 transition-all duration-300 transform hover:scale-105 w-max"
        >
          Voir nos produits
        </Link>
      </div>
      {/*images*/}
      <div className="relative">
        <img
          src={im1}
          alt="Image 1"
          className="w-full h-64 object-cover rounded-lg shadow-lg mb-4"
        />
        <img
          src={im2}
          alt="Image 2"
          className="w-3/4 h-48 object-cover rounded-lg shadow-lg absolute top-32 left-8 border-4 border-white"
        />
        <img
          src={im3}
          alt="Image 3"
          className="w-2/4 h-32 object-cover rounded-lg shadow-lg absolute top-48 left-32 border-4 border-white"
        />
      </div>
    </section>
  );
}

export default Home;