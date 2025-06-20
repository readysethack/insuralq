import React from "react";

const CallToAction: React.FC = () => (
  <section className="py-16 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500 text-white text-center">
    <h2 className="text-3xl md:text-4xl font-bold mb-6">
      Ready to get a second opinion?
    </h2>
    <p className="mb-8 text-lg md:text-xl">
      Sign up as a customer or join the claims investigation team to experience
      AI-powered insurance analysis.
    </p>
    <div className="flex flex-col md:flex-row gap-6 justify-center">
      <a
        href="#auth?role=customer"
        className="px-8 py-3 bg-white text-blue-600 font-bold rounded-lg shadow-lg hover:bg-blue-100 transition"
      >
        Sign Up as Customer
      </a>
      <a
        href="#auth?role=investigator"
        className="px-8 py-3 bg-blue-700 text-white font-bold rounded-lg shadow-lg hover:bg-blue-800 transition"
      >
        Join Investigation Team
      </a>
    </div>
  </section>
);

export default CallToAction;
