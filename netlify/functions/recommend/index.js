const { PythonShell } = require('python-shell');
const path = require('path');

exports.handler = async (event, context) => {
  // Only allow POST requests
  if (event.httpMethod !== 'POST' && event.httpMethod !== 'OPTIONS') {
    return {
      statusCode: 405,
      body: JSON.stringify({ error: 'Method not allowed' }),
    };
  }

  // Handle CORS preflight
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
      },
    };
  }

  try {
    const options = {
      mode: 'text',
      pythonPath: 'python3',
      pythonOptions: ['-u'],
      scriptPath: __dirname,
      args: [JSON.stringify({
        body: event.body,
        httpMethod: event.httpMethod
      })]
    };

    return new Promise((resolve, reject) => {
      PythonShell.run('recommend.py', options, (err, results) => {
        if (err) {
          console.error('Error executing Python script:', err);
          resolve({
            statusCode: 500,
            body: JSON.stringify({ error: 'Internal server error', details: err.message }),
          });
          return;
        }

        try {
          const result = JSON.parse(results[results.length - 1]);
          resolve({
            statusCode: 200,
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': '*',
            },
            body: JSON.stringify(result),
          });
        } catch (e) {
          console.error('Python script output:', results);
          resolve({
            statusCode: 500,
            body: JSON.stringify({ error: 'Invalid response from model' }),
          });
        }
      });
    });
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Server error' }),
    };
  }
};
