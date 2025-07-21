import { Outlet } from "react-router-dom";
import Banner from "./component/Banner";
import "./App.css";

export default function App() {
   return (
      <main>
         <Banner />
         <Outlet />
      </main>
   );
}
