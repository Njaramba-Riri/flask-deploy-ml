import numpy as np
import pickle 

from flask import Flask, request, jsonify

app=Flask(__name__)

#load the model
model=pickle.load(open('model.pkl','rb'))

@app.route('/api',methods=['POST'])
def predict():
    #get data from post request
    data=request.get_json(force=True)
    #make prediction using model loaded from disk as per the data
    prediction=model.predict([[np.array(data['exp'])]])

    #take the first value of prediction
    output=prediction[0]
    return jsonify(output)


if __name__=='__main__':
    app.run(port=5000, debug=True)
