import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import { Amplify } from "aws-amplify";
import { locations } from "../library/constants";
import { getAmplifyConfig } from "../config/getAmplifyConfig";
import React, { useEffect } from "react";

import Home from "./Home";
import Registration from "./Registration";
import SignInSuccess from "./SignInSuccess";
import SignInError from "./SignInError";
import NotFoundPage from "./NotFoundPage";
import VisitForm from "../components/VisitForm";
import Admin from "./Admin";
import Qualifications from "./Qualifications";
import EquipmentForm from "./EquipmentForm";
import Visits from "./Visits";
import EquipmentUsage from "./EquipmentUsage";

const App = () => {
  useEffect(() => {
    const config = getAmplifyConfig();
    Amplify.configure({
      Auth: {
        Cognito: {
          userPoolId: config.userPoolId,
          userPoolClientId: config.userPoolClientId,
        },
      },
    });
  }, []);
  return (
    <Router>
      <Routes>
        {/* Public pages */}
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Registration />} />
        <Route path="/equipment_form" element={<EquipmentForm />} />
        <Route path="/success" element={<SignInSuccess />} />
        <Route path="/error" element={<SignInError />} />
        <Route path="*" element={<NotFoundPage />} />

        {/* Admin pages */}
        <Route path="/admin" element={<Admin />} />
        <Route path="/qualifications" element={<Qualifications />} />
        <Route path="/equipment_usage" element={<EquipmentUsage />} />
        <Route path="/visits" element={<Visits />} />

        {/* makerspace specific routes */}
        {locations.map((location) => {
          const { slug } = location;
          return (
            <Route
              path={`/${slug}`}
              key={slug}
              element={<VisitForm location={location} />}
            />
          );
        })}
      </Routes>
    </Router>
  );
};

export default App;
