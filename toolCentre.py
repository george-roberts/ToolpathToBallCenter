# Author-George Roberts
# Description-Plotting toolpath at ball center

import adsk.core, adsk.cam, adsk.fusion, traceback, tempfile, os

# global set of event handlers to keep them referenced for the duration of the command
handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface

_inputs = adsk.core.CommandInputs.cast(None)
_cgGroups = adsk.fusion.CustomGraphicsGroups.cast(None)

class toolpathCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            global _inputs

        except:
            if ui:
                ui.messageBox('Error:\n{}'.format(traceback.format_exc()))

class ToolpathCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            des = app.activeDocument.products.itemByProductType('DesignProductType')
            root = des.rootComponent
            while root.customGraphicsGroups.count > 0:
                root.customGraphicsGroups.item(0).deleteMe()
                app.activeViewport.refresh()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class ToolpathCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            onExecute = toolpathCommandExecuteHandler()
            cmd.execute.add(onExecute)
            onExecutePreview = toolpathCommandExecuteHandler()
            cmd.executePreview.add(onExecutePreview)
            onDestroy = ToolpathCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            handlers.append(onDestroy)

            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            handlers.append(onExecutePreview)
            product = app.activeProduct
            cam = adsk.cam.CAM.cast(product)
            des = app.activeDocument.products.itemByProductType('DesignProductType')
            if not cam:
                ui.messageBox(
                'It is not supported in current workspace, please change to MFG workspace and try again.')
                return
           
            global _cgGroups
            
            operationToPost = adsk.cam.Operation.cast(None)
            
            for operation in cam.allOperations:
                if operation.isSelected:
                    operationToPost = operation
                    break
            
            if not operationToPost:
                ui.messageBox('Please select an operation from the browser and try again')
                return
            
            tmpDir = tempfile.gettempdir()
            postInput = adsk.cam.PostProcessInput.create('999', os.path.join(os.path.dirname(__file__), 'Resources', 'ballcenter.cps'), tmpDir, adsk.cam.PostOutputUnitOptions.MillimetersOutput)
            postedPath = os.path.join(tmpDir, '999.bcp')
            postInput.isOpenInEditor = False
            if os.path.exists(postedPath):
                os.remove(postedPath)
            try:
                cam.postProcess(operationToPost, postInput)
            except:
                ui.messageBox('Only ball nose tools are supported')
                return
            
            if not os.path.exists(postedPath):
                ui.messageBox("Calculation failed")
            f = open(postedPath, 'r')
            postedLines = f.readline().replace(' ', '').replace('\n','').split(',')
            f.close()
            lineArray = []
            for value in  postedLines:
                try:
                    lineArray.append(float(value))
                except:
                    # not a unit
                    failedUnit = True
            _cgGroups = des.rootComponent.customGraphicsGroups
            cgGroup = adsk.fusion.CustomGraphicsGroup.cast(_cgGroups.add())
            lineCoords = adsk.fusion.CustomGraphicsCoordinates.create(lineArray)
            lines = cgGroup.addLines(lineCoords, [], True)
            color = adsk.fusion.CustomGraphicsSolidColorEffect.create(adsk.core.Color.create(0,0,128,255))
            lines.weight = 1
            lines.color = color
            lines.isSelectable = False
            app.activeViewport.refresh()
            # define the inputs
            global _inputs
            _inputs = adsk.core.CommandInputs.cast(cmd.commandInputs)
            
            stringInp = _inputs.addTextBoxCommandInput('close', 'Toolpath plotted', '<b>Toolpath plotted</b> <br>Close this dialog to clear the screen', 4, True)
            stringInp.isFullWidth = True
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        commandDefinitions = ui.commandDefinitions
        # check the command exists or not
        cmdDef = commandDefinitions.itemById('toolpathPlotter')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('toolpathPlotter',
                                                            'Plot toolpath',
                                                            'Plot toolpath to the ball centre.',
                                                            './/Resources')  # relative resource file path is specified

        toolpathCommandCreated = ToolpathCommandCreatedHandler()
        cmdDef.commandCreated.add(toolpathCommandCreated)
        handlers.append(toolpathCommandCreated)
        solidPanel = ui.allToolbarPanels.itemById('CAMActionPanel')
        solidPanel.controls.addCommand(cmdDef)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface

        if ui.commandDefinitions.itemById('toolpathPlotter'):
            ui.commandDefinitions.itemById('toolpathPlotter').deleteMe()
        solidPanel = ui.allToolbarPanels.itemById('CAMActionPanel')
        cntrl = solidPanel.controls.itemById('toolpathPlotter')
        if cntrl:
            cntrl.deleteMe()

        if cntrl:
            cntrl.deleteMe()
    except:
        pass