import React, { useState } from 'react';  
import { motion } from 'framer-motion';  
import { Upload, Image, Plus } from 'lucide-react';  

const UploadArea = ({ onImageSelect }) => {  
  const [dragActive, setDragActive] = useState(false);  
  const [selectedImage, setSelectedImage] = useState(null);  

  const handleDrag = (e) => {  
    e.preventDefault();  
    e.stopPropagation();  
    if (e.type === "dragenter" || e.type === "dragover") {  
      setDragActive(true);  
    } else if (e.type === "dragleave") {  
      setDragActive(false);  
    }  
  };  

  const handleDrop = (e) => {  
    e.preventDefault();  
    e.stopPropagation();  
    setDragActive(false);  
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {  
      const file = e.dataTransfer.files[0];  
      if (file.type.startsWith('image/')) {  
        const reader = new FileReader();  
        reader.onload = (event) => {  
          setSelectedImage(event.target.result);  
          onImageSelect(file);  
        };  
        reader.readAsDataURL(file);  
      }  
    }  
  };  

  const handleFileSelect = (e) => {  
    const file = e.target.files[0];  
    if (file && file.type.startsWith('image/')) {  
      const reader = new FileReader();  
      reader.onload = (event) => {  
        setSelectedImage(event.target.result);  
        onImageSelect(file);  
      };  
      reader.readAsDataURL(file);  
    }  
  };  

  return (  
    <motion.div  
      className={`relative bg-white/80 backdrop-blur-xl border-2 rounded-3xl p-8 text-center transition-all duration-300 ${  
        dragActive  
          ? 'border-green-400 bg-green-50/50 shadow-2xl shadow-green-200/50 scale-105'  
          : 'border-gray-200/50 hover:border-blue-300 hover:shadow-lg'  
      }`}  
      initial={{ scale: 0.95, opacity: 0 }}  
      animate={{ scale: 1, opacity: 1 }}  
      whileHover={{ scale: 1.02 }}  
      whileTap={{ scale: 0.98 }}  
      transition={{ duration: 0.3, type: "spring", stiffness: 300 }}  
      onDragEnter={handleDrag}  
      onDragLeave={handleDrag}  
      onDragOver={handleDrag}  
      onDrop={handleDrop}  
    >  
      {selectedImage ? (  
        <motion.div  
          className="flex flex-col items-center gap-4"  
          initial={{ opacity: 0, scale: 0.8 }}  
          animate={{ opacity: 1, scale: 1 }}  
          transition={{ duration: 0.4, type: "spring", stiffness: 300 }}  
          exit={{ opacity: 0, scale: 0.8 }}  
        >  
          <motion.img  
            src={selectedImage}  
            alt="Hongo seleccionado"  
            className="w-64 h-64 object-cover rounded-2xl shadow-lg border-4 border-green-200"  
            initial={{ rotate: -5, y: 20 }}  
            animate={{ rotate: 0, y: 0 }}  
            transition={{ duration: 0.5, type: "spring", stiffness: 200 }}  
            whileHover={{ scale: 1.05, rotate: 2 }}  
          />  
          <motion.p  
            className="text-gray-600 font-medium"  
            initial={{ opacity: 0 }}  
            animate={{ opacity: 1 }}  
            transition={{ delay: 0.2, duration: 0.3 }}  
          >  
            ¡Foto lista! Dale al botón para identificar.  
          </motion.p>  
        </motion.div>  
      ) : (  
        <>  
          <motion.div  
            className="mx-auto w-20 h-20 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center mb-6"  
            initial={{ scale: 0.8, opacity: 0 }}  
            animate={{ scale: 1, opacity: 1 }}  
            whileHover={{ scale: 1.1, rotate: 5 }}  
            transition={{ type: "spring", stiffness: 400, damping: 20 }}  
          >  
            <Upload className="w-10 h-10 text-white" />  
          </motion.div>  
          <motion.h2  
            className="text-2xl font-bold text-gray-800 mb-2"  
            initial={{ y: -10, opacity: 0 }}  
            animate={{ y: 0, opacity: 1 }}  
            transition={{ delay: 0.1, duration: 0.3 }}  
          >  
            Sube tu hongo misterioso  
          </motion.h2>  
          <motion.p  
            className="text-gray-600 mb-6"  
            initial={{ y: -10, opacity: 0 }}  
            animate={{ y: 0, opacity: 1 }}  
            transition={{ delay: 0.2, duration: 0.3 }}  
          >  
            Arrastra la imagen aquí o haz clic para elegirla  
          </motion.p>  
          <div className="flex flex-col sm:flex-row gap-4 justify-center">  
            <motion.label  
              htmlFor="file-upload"  
              className="px-6 py-3 bg-blue-500 text-white rounded-2xl font-semibold cursor-pointer hover:bg-blue-600 flex items-center gap-2 justify-center transition-colors"  
              initial={{ scale: 0.95 }}  
              whileHover={{ scale: 1.05 }}  
              whileTap={{ scale: 0.95 }}  
              transition={{ type: "spring", stiffness: 300 }}  
            >  
              <Image className="w-5 h-5" />  
              Elegir foto  
            </motion.label>  
            <input  
              id="file-upload"  
              type="file"  
              accept="image/*"  
              onChange={handleFileSelect}  
              className="hidden"  
            />  
            <motion.div  
              className="px-6 py-3 bg-gray-100 text-gray-600 rounded-2xl font-semibold flex items-center gap-2 justify-center hover:bg-gray-200 transition-colors"  
              initial={{ scale: 0.95 }}  
              whileHover={{ scale: 1.05 }}  
              whileTap={{ scale: 0.95 }}  
              transition={{ type: "spring", stiffness: 300 }}  
            >  
              <Plus className="w-5 h-5" />  
              O arrastra aquí  
            </motion.div>  
          </div>  
        </>  
      )}  
    </motion.div>  
  );  
};  

export default UploadArea;