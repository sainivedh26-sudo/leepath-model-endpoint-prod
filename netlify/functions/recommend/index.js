const { spawnSync } = require('child_process');
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
    // Execute Python script
    const pythonPath = path.join(__dirname, 'recommend.py');
    const process = spawnSync('python3', [pythonPath], {
      input: JSON.stringify({
        body: event.body,
        httpMethod: event.httpMethod
      }),
      encoding: 'utf-8',
    });

    if (process.error) {
      console.error('Error executing Python script:', process.error);
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Internal server error' }),
      };
    }

    // Parse Python output
    try {
      const result = JSON.parse(process.stdout);
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        body: JSON.stringify(result),
      };
    } catch (e) {
      console.error('Python script output:', process.stdout);
      console.error('Python script error:', process.stderr);
      return {
        statusCode: 500,
        body: JSON.stringify({ error: 'Invalid response from model' }),
      };
    }
  } catch (error) {
    console.error('Function error:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: 'Server error' }),
    };
  }
};