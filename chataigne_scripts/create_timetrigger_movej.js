
var sequenceTarget = script.addTargetParameter("Sequence Target", "The target to use for the moveJ command"); 	
var triggerMoveJ = script.addTrigger("Create moveJ", "Creates a moveJ command in the current active sequence"); 									//This will add a trigger (button)

sequenceTarget.setAttribute("root", root.sequences);
sequenceTarget.setAttribute("targetType", "container");
sequenceTarget.setAttribute("searchLevel", 2);


var yPos = 0;



function init()
{


}

/*
 This function will be called each time a parameter of your script has changed
*/
function scriptParameterChanged(param)
{
	if(param.is(triggerMoveJ)){

		var timeCursor = sequenceTarget.getTarget().getParent().getParent().getChild("Current Time").get();

		newTimeTrigger = sequenceTarget.getTarget().getChild("Triggers").addItem();
		newTimeTrigger.getChild("Time").set(timeCursor);
		newTimeTrigger.getChild("Flag Y").set(yPos);
		yPos = (yPos + 0.2 ) ;
		if (yPos > 1.0) {
			yPos = 0.0;
		}


		var consequence = newTimeTrigger.getChild("Consequences").addItem("Consequence");
		
		script.log(consequence.getControllables());

	}
}

//GetControllables output: [[Enabled : Boolean > 1], [MiniMode : Boolean > 0], [ListSize : Float > 24.000], [ViewUIPosition : Point2D > [0.0,0.0]], [ViewUISize : Point2D > [200.0,200.0]], [Locked : Boolean > 0], [Trigger : Trigger]]