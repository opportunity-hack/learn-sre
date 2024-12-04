// src/App.tsx
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { monitoring } from './monitoring';

interface Product {
    id: number;
    name: string;
    price: number;
    stock: number;
}

const BACKEND_URL = window.location.href.includes('-5173.')
    ? window.location.href.replace('-5173.', '-8000.')
    : window.location.origin;

const App = () => {
    const [products, setProducts] = useState<Product[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const startTime = performance.now();
        
        const fetchProducts = async () => {
            try {
                const responses = await Promise.all([
                    axios.get(`${BACKEND_URL}/products/1`),
                    axios.get(`${BACKEND_URL}/products/2`),
                    axios.get(`${BACKEND_URL}/products/3`),                    
                ]);
                
                const duration = performance.now() - startTime;
                monitoring.recordApiLatency('/products', duration);
                monitoring.recordApiResult('/products', true);
                
                const products = responses.map(r => r.data);
                setProducts(products);

                // Add a project that doesn't exist to force an error on purchase
                products.push({ id: 4, name: 'Doesnt Exist', price: 10, stock: 42 });
                
                // Record product availability
                products.forEach(product => {
                    monitoring.recordProductAvailability(product.id, product.stock > 0);
                });
                
            } catch (err) {
                monitoring.recordApiResult('/products', false);
                setError('Failed to fetch products');
                
            } finally {
                setLoading(false);
            }

            // Force an error by fetching a product that doesn't exist - do this outside of the try/catch block to avoid an error on the page
            axios.get(`${BACKEND_URL}/products/doesntexist`).catch(() => {});
        };

        fetchProducts();
    }, []);

    const handlePurchase = async (productId: number) => {        
        try {
            const startTime = performance.now();
            await axios.post(`${BACKEND_URL}/products/${productId}/purchase`);
            
            monitoring.recordApiLatency(`/products/${productId}/purchase`, performance.now() - startTime);
            monitoring.recordPurchaseAttempt(productId, true);
            
            const response = await axios.get(`${BACKEND_URL}/products/${productId}`);
            setProducts(products.map(p => 
                p.id === productId ? response.data : p
            ));
        } catch (err) {        
            monitoring.recordPurchaseAttempt(productId, false);
            setError('Purchase failed');
        }
    };

    // Rest of the component remains the same
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">Product List</h1>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {products.map(product => (
                    <div key={product.id} className="border p-4 rounded shadow">
                        <h2 className="text-xl">{product.name}</h2>
                        <p className="text-gray-600">${product.price}</p>
                        <p className="text-sm">Stock: {product.stock}</p>
                        <button
                            onClick={() => handlePurchase(product.id)}
                            className="mt-2 bg-blue-500 text-white px-4 py-2 rounded"
                        >
                            Purchase
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default App;