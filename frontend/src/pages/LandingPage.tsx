import React from "react";
import {
  HeroSection,
  FeatureShowcase,
  HowItWorks,
  Testimonials,
  CallToAction,
} from "../components/Landing";

const LandingPage: React.FC = () => (
  <div className="w-full min-h-screen bg-gray-50 dark:bg-gray-900">
    <HeroSection />
    <FeatureShowcase />
    <HowItWorks />
    <Testimonials />
    <CallToAction />
  </div>
);

export default LandingPage;
