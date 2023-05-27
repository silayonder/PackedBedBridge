#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback, math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        # ui.messageBox('This is my first script in Fusion Python API')

        # Create a new document.
        # doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des = app.activeProduct
        root = des.rootComponent
        bodies = root.bRepBodies

        # Make sure it is a direct modeling document.
        des.designType = adsk.fusion.DesignTypes.DirectDesignType

        radius = 0.00105
        r2 = radius*0.25

        threShold = radius*0.07
        TankC1 = adsk.core.Point3D.create(0,0,-0.011)
        TankC2 = adsk.core.Point3D.create(0,0,0.011)
        TankRadius = 0.00701

        # Read sphere center positions from files
        x = open('C:/Users/onder/Desktop/UDF1/MyFirstScript/small__X.txt', 'r')
        linesx = x.readlines()

        y = open('C:/Users/onder/Desktop/UDF1/MyFirstScript/small__Y.txt', 'r')
        linesy = y.readlines() 

        z = open('C:/Users/onder/Desktop/UDF1/MyFirstScript/small__Z.txt', 'r')
        linesz = z.readlines()


        tBrep = adsk.fusion.TemporaryBRepManager.get()
        sphereBody = None
        centerArray = []
        lineArray = []
        sphereArray = []
        cylinderArray = []
        wallCylinderArray = []

        # Generate center points
        for i in range(len(linesx)):
            center = adsk.core.Point3D.create(float(linesx[i]),float(linesy[i]),float(linesz[i]))
            line = adsk.core.Point3D.create(0,0,float(linesz[i]))
            centerArray.append(center)
            lineArray.append(line)
 
            # Generate spheres
            sphereBody = tBrep.createSphere(center, radius)
            sphereArray.append(sphereBody)


        # Generate cylinder between spheres
        for i in range(len(centerArray)):
            for j in range(len(centerArray)):
                if i ==j:
                    continue
                p1 = centerArray[i]
                p2 = centerArray[j]
                distance = p1.distanceTo(p2) 
                # math.sqrt((p1.x-p2.x)**2 + (p1.y-p2.y)**2 + (p1.z-p2.z)**2)
                # DirVec = adsk.core.Vector3D.create((p1.x-p2.x),(p1.y-p2.y),(p1.z-p2.z))
                DirVec = p1.vectorTo(p2)
                DirVec.normalize()
                DirVec_rad = adsk.core.Vector3D.create(DirVec.x * radius * 0.6, DirVec.y * radius * 0.6, DirVec.z * radius * 0.6)

                DirVec_rad_pt = adsk.core.Point3D.create(DirVec_rad.x, DirVec_rad.y, DirVec_rad.z)
                p1_translated = adsk.core.Point3D.create((p1.x - DirVec_rad_pt.x), (p1.y - DirVec_rad_pt.y), (p1.z - DirVec_rad_pt.z))
                p2_translated = adsk.core.Point3D.create((p2.x + DirVec_rad_pt.x), (p2.y + DirVec_rad_pt.y), (p2.z + DirVec_rad_pt.z))

                if (distance - 2*radius) <= threShold:
                    cylinder = tBrep.createCylinderOrCone(p1_translated,r2,p2_translated,r2)
                    cylinderArray.append(cylinder)                

        # Generate cylinder bed
        TankCylinder = tBrep.createCylinderOrCone(TankC1,TankRadius,TankC2,TankRadius)
        body3 = bodies.add(TankCylinder)
        body3.name = 'Tank Cylinder'

        # Generate cylinder between bed wall and spheres
        for i in range(len(centerArray)):
            c1 = centerArray[i]
            dist1 = abs(math.sqrt((c1.x)**2 + (c1.y)**2))
            dist2 = TankRadius - dist1 - radius
            DirVec2 = c1.asVector()
            DirVec2.z = 0
            DirVec2 = adsk.core.Vector3D.create(c1.x, c1.y, 0)
            DirVec2.normalize()
            DirVec_rad2 = adsk.core.Vector3D.create((DirVec2.x*radius*0.6),(DirVec2.y)*radius*0.6,(DirVec2.z)*radius*0.6)
            DirVec_rad3 = adsk.core.Vector3D.create((DirVec2.x*radius*1.5),(DirVec2.y)*radius*1.5,(DirVec2.z)*radius*1.5)
            DirVec_rad_pt2 = adsk.core.Point3D.create(DirVec_rad2.x, DirVec_rad2.y, DirVec_rad2.z)
            DirVec_rad_pt3 = adsk.core.Point3D.create(DirVec_rad3.x, DirVec_rad3.y, DirVec_rad3.z)
            c2_translated = adsk.core.Point3D.create((c1.x + DirVec_rad_pt3.x), (c1.y + DirVec_rad_pt3.y), (c1.z + DirVec_rad_pt2.z))

            if dist2 <= threShold:
                wallcylinder = tBrep.createCylinderOrCone(c1,r2,c2_translated,r2)
                wallCylinderArray.append(wallcylinder)


        # Union all of the created objects
        sp = sphereArray[0]
        union = adsk.fusion.BooleanTypes.UnionBooleanType 
        for i in range(1, len(sphereArray)):
            tBrep.booleanOperation(sp, sphereArray[i], union)

        for i in range(len(cylinderArray)):
            tBrep.booleanOperation(sp, cylinderArray[i], union)

        for i in range(len(wallCylinderArray)):
            tBrep.booleanOperation(sp, wallCylinderArray[i], union)
        
        body = bodies.add(sp)
        body.name = 'Booleaned Bodies'

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))