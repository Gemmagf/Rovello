import React from 'react';  
import { motion } from 'framer-motion';  
import { AlertCircle, CheckCircle, Heart, X, Loader2 } from 'lucide-react';  

const ResultDisplay = ({ result, isLoading }) => {  
  if (isLoading) {  
    return (  
      <motion.div  
        className="bg-white/80 backdrop-blur-xl border border-gray-200/50 rounded-3xl p-8 text-center shadow-xl flex flex-col items-center justify-center"  
        initial={{ opacity: 0, scale: 0.9 }}  
        animate={{ opacity: 1, scale: 1 }}  
        exit={{ opacity: 0, scale: 0.9 }}  
        transition={{ duration: 0.5, ease: "easeInOut" }}  
      >  
        <motion.div  
          animate={{  
            rotate: 360  
          }}  
          transition={{  
            duration: 1,  
            repeat: Infinity,  
            ease: "linear"  
          }}  
          className="relative w-16 h-16 mb-4"  
        >  
          <Loader2 className="w-16 h-16 text-purple-500 absolute" />  
          <motion.div  
            className="w-16 h-16 border-4 border-purple-200/50 rounded-full absolute"  
            animate={{  
              rotate: -360,  
              scale: [1, 1.1, 1],  
            }}  
            transition={{  
              duration: 1.5,  
              repeat: Infinity,  
              ease: "easeInOut"  
            }}  
          />  
        </motion.div>  
        <motion.p  
          className="text-gray-600 font-semibold mb-2"  
          initial={{ opacity: 0, y: 10 }}  
          animate={{ opacity: 1, y: 0 }}  
          transition={{ delay: 0.2, duration: 0.3 }}  
        >  
          ¡Magia setácea en acción!  
        </motion.p>  
        <motion.p  
          className="text-gray-500 text-sm"  
          initial={{ opacity: 0, y: 10 }}  
          animate={{ opacity: 1, y: 0 }}  
          transition={{ delay: 0.4, duration: 0.3 }}  
        >  
          Analizando tu hongo misterioso... un poquito más de paciencia, ¡va a ser épico!  
        </motion.p>  
      </motion.div>  
    );  
  }  

  if (!result) return null;  

  const isEdible = result.edible;  

  return (  
    <motion.div  
      className={`bg-white/90 backdrop-blur-xl border rounded-3xl p-6 shadow-xl overflow-hidden ${  
        isEdible ? 'border-green-200' : 'border-red-200'  
      }`}  
      initial={{ opacity: 0, y: 50, scale: 0.8 }}  
      animate={{ opacity: 1, y: 0, scale: 1 }}  
      exit={{ opacity: 0, y: -50, scale: 0.8 }}  
      transition={{  
        type: "spring",  
        stiffness: 300,  
        damping: 30,  
        duration: 0.6  
      }}  
    >  
      <motion.div  
        className="flex items-start gap-4 mb-4"  
        initial={{ opacity: 0 }}  
        animate={{ opacity: 1 }}  
        transition={{ delay: 0.2 }}  
      >  
        {isEdible ? (  
          <motion.div  
            className="flex-shrink-0"  
            initial={{ scale: 0, rotate: -180 }}  
            animate={{ scale: 1, rotate: 0 }}  
            transition={{ type: "spring", stiffness: 200 }}  
          >  
            <CheckCircle className="w-8 h-8 text-green-500 mt-1" />  
          </motion.div>  
        ) : (  
          <motion.div  
            className="flex-shrink-0"  
            initial={{ scale: 0, rotate: 180 }}  
            animate={{ scale: 1, rotate: 0 }}  
            transition={{ type: "spring", stiffness: 200 }}  
          >  
            <AlertCircle className="w-8 h-8 text-red-500 mt-1" />  
          </motion.div>  
        )}  
        <div className="flex-1 min-w-0">  
          <motion.h3  
            className="text-xl font-bold text-gray-800 mb-1"  
            initial={{ x: -20 }}  
            animate={{ x: 0 }}  
            transition={{ delay: 0.3, duration: 0.4 }}  
          >  
            {result.name}  
          </motion.h3>  
          <motion.p  
            className="text-gray-600 mb-3"  
            initial={{ x: -20, opacity: 0 }}  
            animate={{ x: 0, opacity: 1 }}  
            transition={{ delay: 0.4, duration: 0.4 }}  
          >  
            {result.description}  
          </motion.p>  
          <motion.div  
            className="flex items-center gap-4 text-sm"  
            initial={{ y: 20, opacity: 0 }}  
            animate={{ y: 0, opacity: 1 }}  
            transition={{ delay: 0.5, duration: 0.3 }}  
          >  
            <motion.span  
              className={`px-3 py-1 rounded-full font-semibold ${  
                isEdible ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'  
              }`}  
              whileHover={{ scale: 1.05 }}  
            >  
              {isEdible ? '🍄 Comestible' : '☠️ Tóxico'}  
            </motion.span>  
            <span className="flex items-center gap-1 text-gray-500">  
              {isEdible ? <Heart className="w-4 h-4" /> : <X className="w-4 h-4" />}  
              {result.toxicity || 'Nivel de riesgo'}  
            </span>  
          </motion.div>  
        </div>  
      </motion.div>  
      {result.tips && (  
        <motion.div  
          className="bg-gray-50/50 p-4 rounded-2xl"  
          initial={{ height: 0, opacity: 0 }}  
          animate={{ height: "auto", opacity: 1 }}  
          transition={{ delay: 0.6, duration: 0.4 }}  
        >  
          <h4 className="font-semibold text-gray-700 mb-2">Consejo del experto:</h4>  
          <p className="text-sm text-gray-600">{result.tips}</p>  
        </motion.div>  
      )}  
    </motion.div>  
  );  
};  

export default ResultDisplay;