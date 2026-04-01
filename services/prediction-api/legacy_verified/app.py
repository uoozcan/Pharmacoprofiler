from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

from rdkit import Chem 
from rdkit.Chem import AllChem
import joblib
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

class PIC50Predictor:
    def __init__(self):
        self.omics_file = None
        self.cl_dict_file = None
        self.loaded_model = None
        self.cl_tissue_dict = None
        self.cl_rrid_dict = None
        self.cl_main_dict = None
        self.main_cl_list = None
        self.is_loaded = False
    
    def load_model_and_data(self):
        """Load the model and required data files"""
        try:
            logger.info("Loading model and data files...")
            
            # Load data files
            self.omics_file = pd.read_csv(
                "GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt", 
                delimiter="\t"
            )
            self.cl_dict_file = pd.read_csv(
                "GDSC_988_cell_line_name_main_fix_RRID_v1.txt", 
                delimiter="\t"
            )
            self.loaded_model = joblib.load("GDSC_CCLE_cross_domain_mode_7_v4.joblib")
            
            # Setup dictionaries
            self.cl_dict_file.rename(columns={"edited":"CELL_LINE_NAME"}, inplace=True)
            self.main_cl_list = self.cl_dict_file.CELL_LINE_NAME.tolist()
            
            # Create dictionaries for cell line mapping and metadata
            self.cl_main_dict = dict(zip(self.cl_dict_file.CELL_LINE_NAME, self.cl_dict_file.main))
            self.cl_tissue_dict = dict(zip(self.cl_dict_file.CELL_LINE_NAME, self.cl_dict_file.TISSUE))
            self.cl_rrid_dict = dict(zip(self.cl_dict_file.CELL_LINE_NAME, self.cl_dict_file.RRID))
            
            self.is_loaded = True
            logger.info(f"Successfully loaded {len(self.main_cl_list)} cell lines")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model and data: {e}")
            return False
    
    def smiles_to_ecfp4(self, smiles_string):
        """Convert SMILES to ECFP4 1024-bit fingerprint"""
        try:
            mol = Chem.MolFromSmiles(smiles_string.strip())
            if mol is None:
                return None
            ecfp4_fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius=2, nBits=1024)
            return [int(bit) for bit in ecfp4_fp.ToBitString()]
        except Exception as e:
            logger.error(f"Error converting SMILES to ECFP4: {e}")
            return None
    
    def predict_batch(self, smiles_list):
        """Predict pIC50 for multiple SMILES"""
        if not self.is_loaded:
            return {"error": "Model not loaded"}
        
        # Process each SMILES
        valid_compounds = []
        invalid_smiles = []
        
        for smiles in smiles_list:
            if not isinstance(smiles, str) or not smiles.strip():
                invalid_smiles.append({
                    "smiles": smiles,
                    "error": "Invalid or empty SMILES string"
                })
                continue
            
            ecfp4_bits = self.smiles_to_ecfp4(smiles)
            if ecfp4_bits is not None:
                valid_compounds.append({
                    "smiles": smiles,
                    "ecfp4": ecfp4_bits
                })
            else:
                invalid_smiles.append({
                    "smiles": smiles,
                    "error": "Could not parse SMILES"
                })
        
        if not valid_compounds:
            return {
                "total_smiles_submitted": len(smiles_list),
                "valid_smiles_count": 0,
                "invalid_smiles_count": len(invalid_smiles),
                "predictions": {},
                "total_predictions": 0,
                "invalid_smiles": invalid_smiles
            }
        
        # Create feature matrix
        all_data = []
        for compound in valid_compounds:
            for cell_line in self.main_cl_list:
                omics_row = self.omics_file[self.omics_file['CELL_LINE_NAME'] == cell_line]
                if not omics_row.empty:
                    omics_features = omics_row.drop('CELL_LINE_NAME', axis=1).iloc[0].values
                    combined_features = list(omics_features) + compound['ecfp4']
                    
                    all_data.append({
                        'smiles': compound['smiles'],
                        'cell_line': cell_line,
                        'features': combined_features
                    })
        
        # Make predictions
        if all_data:
            feature_matrix = np.array([row['features'] for row in all_data], dtype=np.float32)
            predictions = self.loaded_model.predict(feature_matrix)
            
            # Group results by SMILES
            grouped_predictions = {}
            for i, data_row in enumerate(all_data):
                smiles = data_row['smiles']
                cell_line = data_row['cell_line']
                
                if smiles not in grouped_predictions:
                    grouped_predictions[smiles] = []
                
                grouped_predictions[smiles].append({
                    "CELL_LINE_NAME": self.cl_main_dict.get(cell_line, cell_line),
                    "RRID": self.cl_rrid_dict.get(cell_line, ""),
                    "TISSUE": self.cl_tissue_dict.get(cell_line, ""),
                    "pIC50_Prediction": float(predictions[i])
                })
        else:
            grouped_predictions = {}
            predictions = []
        
        # Return formatted result
        result = {
            "total_smiles_submitted": len(smiles_list),
            "valid_smiles_count": len(valid_compounds),
            "invalid_smiles_count": len(invalid_smiles),
            "predictions": grouped_predictions,
            "total_predictions": len(predictions) if predictions is not None else 0
        }
        
        if invalid_smiles:
            result["invalid_smiles"] = invalid_smiles
        
        return result

# Global predictor instance
predictor = PIC50Predictor()

# API Routes
@app.route('/', methods=['GET'])
def home():
    """API documentation endpoint"""
    return jsonify({
        'service': 'pIC50 Prediction API',
        'version': '1.0.0',
        'status': 'running',
        'model_loaded': predictor.is_loaded,
        'endpoints': {
            'POST /api/predict': 'Predict pIC50 values from SMILES',
            'GET /api/health': 'Health check',
            'GET /api/info': 'Model information',
            'GET /': 'API documentation'
        },
        'usage': {
            'single_smiles': {
                'url': '/api/predict',
                'method': 'POST',
                'content_type': 'application/json',
                'body': {
                    'smiles': 'C(CC(=O)N)CN=C(N)N'
                }
            },
            'multiple_smiles': {
                'url': '/api/predict',
                'method': 'POST',
                'content_type': 'application/json',
                'body': {
                    'smiles': ['C(CC(=O)N)CN=C(N)N', 'CC(C)CC(C(=O)O)N']
                }
            }
        },
        'response_format': {
            'total_smiles_submitted': 'int',
            'valid_smiles_count': 'int',
            'invalid_smiles_count': 'int',
            'total_predictions': 'int',
            'predictions': {
                'SMILES_STRING': [
                    {
                        'CELL_LINE_NAME': 'string',
                        'RRID': 'string',
                        'TISSUE': 'string',
                        'pIC50_Prediction': 'float'
                    }
                ]
            },
            'invalid_smiles': [
                {
                    'smiles': 'string',
                    'error': 'string'
                }
            ]
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': predictor.is_loaded,
        'cell_lines_count': len(predictor.main_cl_list) if predictor.main_cl_list else 0,
        'service': 'pIC50 Prediction API',
        'version': '1.0.0'
    })

@app.route('/api/info', methods=['GET'])
def info():
    """Get detailed model information"""
    if not predictor.is_loaded:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({
        'model_info': {
            'dataset': 'GDSC (Genomics of Drug Sensitivity in Cancer)',
            'cell_lines_count': len(predictor.main_cl_list),
            'omics_features': predictor.omics_file.shape[1] - 1,  # -1 for CELL_LINE_NAME
            'ecfp4_features': 1024,
            'total_features': predictor.omics_file.shape[1] - 1 + 1024,
            'available_tissues': len(set(predictor.cl_tissue_dict.values()))
        },
        'fingerprint_info': {
            'type': 'ECFP4',
            'radius': 2,
            'bits': 1024,
            'library': 'RDKit'
        },
        'performance_limits': {
            'max_smiles_per_request': 'No hard limit (recommended: <10 for performance)',
            'prediction_time': 'Varies by number of SMILES (approx. 1-5 seconds per SMILES)'
        }
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Extract SMILES - support both single string and list
        smiles_input = data.get('smiles')
        if smiles_input is None:
            return jsonify({'error': 'Missing "smiles" field in request'}), 400
        
        # Handle both string and list inputs
        if isinstance(smiles_input, str):
            smiles_list = [smiles_input]
        elif isinstance(smiles_input, list):
            smiles_list = smiles_input
        else:
            return jsonify({'error': 'SMILES must be a string or list of strings'}), 400
        
        if not smiles_list:
            return jsonify({'error': 'No SMILES strings provided'}), 400
        
        # Optional: Limit number of SMILES for performance
        max_smiles = int(os.environ.get('MAX_SMILES_PER_REQUEST', 10))
        if len(smiles_list) > max_smiles:
            return jsonify({
                'error': f'Too many SMILES strings. Maximum allowed: {max_smiles}, provided: {len(smiles_list)}'
            }), 400
        
        # Make prediction
        result = predictor.predict_batch(smiles_list)
        
        # Add metadata
        result['api_version'] = '1.0.0'
        result['request_timestamp'] = pd.Timestamp.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in prediction endpoint: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/predict/single', methods=['POST'])
def predict_single():
    """Convenience endpoint for single SMILES prediction"""
    try:
        data = request.get_json()
        
        if not data or 'smiles' not in data:
            return jsonify({'error': 'Missing "smiles" field in request'}), 400
        
        smiles = data['smiles']
        if not isinstance(smiles, str):
            return jsonify({'error': 'SMILES must be a string'}), 400
        
        # Use the batch prediction with single SMILES
        result = predictor.predict_batch([smiles])
        
        # Add metadata
        result['api_version'] = '1.0.0'
        result['request_timestamp'] = pd.Timestamp.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in single prediction endpoint: {e}")
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation at /',
        'available_endpoints': [
            'GET /',
            'GET /api/health', 
            'GET /api/info',
            'POST /api/predict',
            'POST /api/predict/single'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please try again later.'
    }), 500

def initialize_application():
    """Initialize the application on startup"""
    logger.info("Initializing pIC50 Prediction API...")
    if predictor.load_model_and_data():
        logger.info("API ready to serve requests")
        return True
    else:
        logger.error("Failed to initialize API")
        return False

if __name__ == '__main__':
    # Initialize application
    if initialize_application():
        port = int(os.environ.get('PORT', 5000))
        host = os.environ.get('HOST', '0.0.0.0')
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        logger.info(f"Starting pIC50 Prediction API on {host}:{port}")
        app.run(host=host, port=port, debug=debug)
    else:
        logger.error("Failed to initialize application. Exiting...")
        exit(1)
