import React from 'react';  
import { motion } from 'framer-motion';  
import { Clock, Shield } from 'lucide-react';  

const ResultsPlaceholder = () => {  
  return (  
    <motion.div  
      className="bg-white/80 backdrop-blur-xl border border-gray-200/50 rounded-3xl p-12 text-center shadow-xl"  
      initial={{ opacity: 0, y: 20 }}  
      animate={{ opacity: 1, y: 0 }}  
      transition={{ duration: 0.5 }}  
    >  
      <motion.div  
        className="w-24 h-24 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-6"  
        whileHover={{ scale: 1.1, rotate: 5 }}  
      >  
        <Shield className="w-12 h-12 text-indigo-500" />  
      </motion.div>  
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Listo para el escaneo</h2>  
      <p className="text-gray-500 mb-6">Una vez que subas la foto y pulses analizar, te diré qué boleto es este enigma. ¡No te lo pierdas!</p>  
      <Clock className="w-8 h-8 text-gray-400 mx-auto" />  
    </motion.div>  
  );  
};  

export default ResultsPlaceholder;