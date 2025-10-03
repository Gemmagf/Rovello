import React, { useState } from 'react';  
import { motion, AnimatePresence } from 'framer-motion';  
import Header from './components/Header';  
import UploadArea from './components/UploadArea';  
import AnalyzeButton from './components/AnalyzeButton';  
import ResultDisplay from './components/ResultDisplay';  
import { analyzeMushroom } from './utils/mushroomAnalyzer';  

const App = () => {  
  const [selectedFile, setSelectedFile] = useState(null);  
  const [result, setResult] = useState(null);  
  const [isAnalyzing, setIsAnalyzing] = useState(false);  

  const handleImageSelect = (file) => {  
    setSelectedFile(file);  
    setResult(null); // Limpiar resultado anterior  
  };  

  const handleAnalyze = async () => {  
    if (!selectedFile) return;  
    setIsAnalyzing(true);  
    setResult(null); // Limpiar mientras analiza  
    try {  
      const analysis = await analyzeMushroom(selectedFile);  
      setResult(analysis);  
    } catch (error) {  
      console.error('Error en análisis:', error);  
      setResult({  
        name: "Error en la detección",  
        description: "Algo salió mal. Intenta con otra foto más clara.",  
        edible: false,  
        toxicity: "Revisar imagen",  
        tips: "Asegúrate de que la foto sea nítida y bien iluminada."  
      });  
    } finally {  
      setIsAnalyzing(false);  
    }  
  };  

  return (  
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-green-50 to-teal-50 py-8">  
      <div className="container mx-auto px-4 max-w-2xl">  
        <motion.div  
          initial={{ opacity: 0 }}  
          animate={{ opacity: 1 }}  
          transition={{ duration: 0.8, ease: "easeOut" }}  
        >  
          <Header />  

          <div className="space-y-6 mt-8">  
            <AnimatePresence mode="wait">  
              <UploadArea key="upload" onImageSelect={handleImageSelect} />  
            </AnimatePresence>  

            {selectedFile && (  
              <AnimatePresence>  
                <motion.div  
                  initial={{ y: 20, opacity: 0 }}  
                  animate={{ y: 0, opacity: 1 }}  
                  exit={{ y: -20, opacity: 0 }}  
                  transition={{ duration: 0.3 }}  
                >  
                  <AnalyzeButton  
                    onAnalyze={handleAnalyze}  
                    isAnalyzing={selectedFile && !isAnalyzing}  
                    disabled={isAnalyzing}  
                  />  
                </motion.div>  
              </AnimatePresence>  
            )}  

            <AnimatePresence mode="wait">  
              <ResultDisplay  
                key={result ? 'result' : 'loading'}  
                result={result}  
                isLoading={isAnalyzing}  
              />  
            </AnimatePresence>  
          </div>  
        </motion.div>  

        <motion.div  
          className="mt-12 text-center text-gray-500 text-sm"  
          initial={{ opacity: 0, y: 10 }}  
          animate={{ opacity: 1, y: 0 }}  
          transition={{ delay: 1 }}  
        >  
          Recuerda: Esto es solo para diversión e info básica. Consulta a un experto para lo serio.  
        </motion.div>  
      </div>  
    </div>  
  );  
};  

export default App;