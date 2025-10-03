import React from 'react';  
import { motion } from 'framer-motion';  
import { Play, Shield, Loader2 } from 'lucide-react';  

const AnalyzeButton = ({ onAnalyze, isAnalyzing, disabled }) => {  
  return (  
    <motion.button  
      onClick={onAnalyze}  
      disabled={disabled || !isAnalyzing}  
      className={`w-full md:w-auto px-8 py-4 rounded-2xl font-bold text-lg flex items-center gap-3 justify-center transition-all duration-300 relative overflow-hidden group ${  
        disabled || !isAnalyzing  
          ? 'bg-gray-300 text-gray-500 cursor-not-allowed'  
          : 'bg-gradient-to-r from-purple-500 to-pink-600 text-white shadow-lg hover:shadow-xl active:shadow-inner'  
      }`}  
      initial={{ opacity: 0, y: 20 }}  
      animate={{ opacity: 1, y: 0 }}  
      whileHover={!disabled && isAnalyzing ? { scale: 1.05 } : {}}  
      whileTap={!disabled && isAnalyzing ? { scale: 0.95 } : {}}  
      transition={{ duration: 0.3, type: "spring" }}  
    >  
      {isAnalyzing ? (  
        <motion.div  
          className="flex items-center gap-3"  
          animate={{  
            opacity: [0.5, 1, 0.5],  
            scale: [1, 1.1, 1]  
          }}  
          transition={{  
            duration: 1.5,  
            repeat: Infinity,  
            ease: "easeInOut"  
          }}  
        >  
          <Loader2 className="w-6 h-6 animate-spin text-white" />  
          <span>Analizando magia...</span>  
        </motion.div>  
      ) : (  
        <motion.span  
          className="flex items-center gap-3"  
          whileHover={{ scale: 1.02 }}  
        >  
          <Play className="w-6 h-6" />  
          ¡Identificar hongo!  
        </motion.span>  
      )}  
      {/* Efecto de ondas para el análisis */}  
      {isAnalyzing && (  
        <motion.div  
          className="absolute inset-0 bg-white/20 rounded-2xl"  
          initial={{ scale: 0, opacity: 1 }}  
          animate={{  
            scale: [1, 1.5, 2],  
            opacity: [1, 0.5, 0]  
          }}  
          transition={{  
            duration: 1.5,  
            repeat: Infinity,  
            ease: "easeOut"  
          }}  
        />  
      )}  
    </motion.button>  
  );  
};  

export default AnalyzeButton;