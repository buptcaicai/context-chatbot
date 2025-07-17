import { Outlet } from "react-router-dom";
import Banner from "./component/Banner";

export default function App() {
   return (
      <main>
         <Banner />
         <Outlet />
      </main>
   );
}
