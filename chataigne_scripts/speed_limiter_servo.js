


var maxSpeed = script.addFloatParameter("max Speed","maximum speed in degrees /s", 180,0,360); 		//This will add a float number parameter (slider), default value of 0.1, with a range between 0 and 1


var previousInputs = [];

function filter(inputs, minValues, maxValues, multiplexIndex)
{

	var dT = 1 / 50; // Assuming 50Hz update rate

	var result = [];
	for(var i = 0; i < inputs.length; i++)
	{
		if (previousInputs.length <= i) {
			previousInputs[i] = inputs[i]; //Initialize previousInputs array if needed
		}

		var error = inputs[i] - previousInputs[i]; 

		var dError = error / dT;

		if (Math.abs(dError) > maxSpeed.get()) { // Threshold for maximum speed
			if (dError > 0) {
				result[i] = previousInputs[i] + maxSpeed.get() * dT; // Limit the increase
			} else {
				result[i] = previousInputs[i] - maxSpeed.get() * dT;
			}
		} else {
			result[i] = inputs[i];
		}
		

		previousInputs[i] = result[i]; //Store the current input value in the previousInputs array for next frame
	}


	return result;
}
