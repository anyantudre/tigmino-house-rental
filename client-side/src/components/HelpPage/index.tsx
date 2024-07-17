import React, { useState } from "react";
import Footer from "../Footer";
import H1Title from "../../Shared/H1Title";
import Header from "../Header";
import { motion } from "framer-motion";

import { Animation } from "../../Shared/Animations";


function HelpPage() {

  const data = [
    {
      question: "How do I book a home",
      answer: "Open a listing, choose your dates on the calendar and the number of guests, then click Book. You need to be signed in.",
    },
    {
      question: "How is the total price calculated",
      answer: "Prices are per night, in Moroccan dirhams (MAD). The total adds a 5% TIGMINO fee, and you see it before you book.",
    },
    {
      question: "How do I contact a host",
      answer: "Click Contact Host on the listing. It opens a real-time chat, and your conversations stay in your Inbox.",
    },
    {
      question: "How do I become a host",
      answer: "Sign in, then use the Add property icon in the header or the Listings tab of your dashboard to publish your home.",
    },
    {
      question: "Where can I see my bookings",
      answer: "Under My Reservations in the profile menu, and in the Bookings tab of your dashboard.",
    },
  ];

  // Define state to track which questions are clicked
  const [questionClicked, setQuestionClicked] = useState(Array(data.length).fill(false));

  // Function to toggle the visibility of a question's answer
  const toggleQuestion = (index) => {
    setQuestionClicked(prevState => {
      const newQuestionClicked = [...prevState];
      newQuestionClicked[index] = !newQuestionClicked[index];
      // Close all other questions
      for (let i = 0; i < newQuestionClicked.length; i++) {
        if (i !== index) {
          newQuestionClicked[i] = false;
        }
      }
      return newQuestionClicked;
    });
  };
  
  return (
    <section className="mx-auto flex flex-col items-center">
      {/* <Header /> */}
      <div className="w-5/6 px-6 py-20">
        <div className="">
          <H1Title styling="mb-5">
            <p>Frequently Asked Questions</p>
          </H1Title>
          {data.map((qa, index) => (
            <motion.div 
              key={index} 
              className="py-1"
              initial={Animation.initial}
              whileInView={Animation.whileInView}
              viewport={Animation.viewport}
              transition={Animation.transition}
              variants={Animation.variants}
            >
              <button
                className="w-full bg-black/90 flex  text-white font-bold px-8 py-3 rounded shadow-lg transition duration-300 ease-in-out transform hover:scale-105"
                onClick={() => toggleQuestion(index)}
              >
                <p>{`${qa.question}?`}</p>
                <span className="ml-auto">{questionClicked[index] ? "-" : "+"}</span>
              </button>
              <div
                className={`mt-2 bg-saffron text-white font-semibold px-4 py-3 rounded shadow-lg transition duration-500 ease-in-out ${
                  questionClicked[index] ? "h-auto" : "h-0 hidden"
                }`}
              >
                <p>{qa.answer}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
      <Footer />
    </section>
  );
}

export default HelpPage;
