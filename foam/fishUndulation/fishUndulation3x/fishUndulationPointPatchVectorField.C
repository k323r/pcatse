/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 1991-2008 OpenCFD Ltd.
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software; you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by the
    Free Software Foundation; either version 2 of the License, or (at your
    option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM; if not, write to the Free Software Foundation,
    Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

\*---------------------------------------------------------------------------*/

#include "fishUndulationPointPatchVectorField.H"
#include "pointPatchFields.H"
#include "addToRunTimeSelectionTable.H"
#include "Time.H"
#include "polyMesh.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

fishUndulationPointPatchVectorField::
fishUndulationPointPatchVectorField
(
    const pointPatch& p,
    const DimensionedField<vector, pointMesh>& iF
)
:
//    fixedValuePointPatchVectorField(p, iF),
  fixedValuePointPatchField<vector>(p, iF), //For OF-1.7.x!!!!!!!!!!!!!!!!!!!!!!
    p0_(p.localPoints()),
    origin_(vector::zero),
    dX_(0.0),
    omega_(0.0),
    length_(0.0),
    waveLength_(0.0),
    a_(0.0),
    b_(0.0),
    c_(0.0)
{}



fishUndulationPointPatchVectorField::
fishUndulationPointPatchVectorField
(
    const pointPatch& p,
    const DimensionedField<vector, pointMesh>& iF,
    const dictionary& dict
)
:
//    fixedValuePointPatchVectorField(p, iF, dict),
  fixedValuePointPatchField<vector>(p, iF, dict), //For OF-1.7.x instead!!!!!!!!
    origin_(dict.lookup("origin")),
    dX_(readScalar(dict.lookup("dX"))),
    omega_(readScalar(dict.lookup("omega"))),
    length_(readScalar(dict.lookup("length"))),
    waveLength_(readScalar(dict.lookup("waveLength"))),
    a_(readScalar(dict.lookup("a"))),
    b_(readScalar(dict.lookup("b"))),
    c_(readScalar(dict.lookup("c")))
{
    if (!dict.found("value"))
    {
        updateCoeffs();
    }

    if (dict.found("p0"))
    {
        p0_ = vectorField("p0", dict , p.size());
    }
    else
    {
        p0_ = p.localPoints();
    }
}


fishUndulationPointPatchVectorField::
fishUndulationPointPatchVectorField
(
    const fishUndulationPointPatchVectorField& ptf,
    const pointPatch& p,
    const DimensionedField<vector, pointMesh>& iF,
//    const PointPatchFieldMapper& mapper
    const pointPatchFieldMapper& mapper //For OF-1.7.x instead!!!!!!!!!!!!!!!!!!
)
:
//    fixedValuePointPatchVectorField(ptf, p, iF, mapper),
    fixedValuePointPatchField<vector>(ptf, p, iF, mapper), //For OF-1.7.x!!!!!!!
    p0_(ptf.p0_),
    origin_(ptf.origin_),
    dX_(ptf.dX_),
    omega_(ptf.omega_),
    length_(ptf.length_),
    waveLength_(ptf.waveLength_),
    a_(ptf.a_),
    b_(ptf.b_),
    c_(ptf.c_)
{}



fishUndulationPointPatchVectorField::
fishUndulationPointPatchVectorField
(
    const fishUndulationPointPatchVectorField& ptf,
    const DimensionedField<vector, pointMesh>& iF
)
:
//    fixedValuePointPatchVectorField(ptf, iF),
  fixedValuePointPatchField<vector>(ptf, iF), //For OF-1.7.x!!!!!!!!!!!!!!!!!!!!
    p0_(ptf.p0_),
    origin_(ptf.origin_),
    dX_(ptf.dX_),
    omega_(ptf.omega_),
    length_(ptf.length_),
    waveLength_(ptf.waveLength_),
    a_(ptf.a_),
    b_(ptf.b_),
    c_(ptf.c_)
{}


// * * * * * * * * * * * * * * * Member Functions  * * * * * * * * * * * * * //

void fishUndulationPointPatchVectorField::updateCoeffs()
{

	// Test if the coefficients have been updated already.
	if (this->updated())
	{
		return;
	}

	const polyMesh& mesh = this->dimensionedInternalField().mesh()();
	const Time& t = mesh.time();


	Info << "Using amplitude function A = " << a_ << "*x² + " << b_ << "*x + " << c_ << endl;


	// Patch relative to the given origin is created in order to obtain a coordinate system starting at 0 0 0 at the fish's head.
	vectorField pointPatchOriginal = p0_ - origin_;


	// The displacement vector field is declared using the undeformed patch.
	//vectorField pointPatchDisplacement = pointPatchOriginal;
	vectorField pointPatchDisplacement(pointPatchOriginal.size(), vector(0,0,0));


	// Declare vector for an individual point of the patch.
	vector pointOriginal;


	// Vector for an individual displacement value is declared.
	vector pointDisplacement = vector(0,0,0);


	// Scalar for the accumulated diplacement in x-direction due to undulation is declared.
	scalar deltaXsum = 0;


	// Calculate the phase shift in radians according to the given wave lengths per bodylength.
	scalar phi = 2 * 3.1415 * length_ / waveLength_;
	Info << "Ratio body length / wave length = " << length_/waveLength_ << endl;

	// Number of center line points.
	int nPoints;

// *****************************************************************************
// Create and move the center line of the fish. ********************************
// *****************************************************************************

	// Number of points.
	nPoints = length_ / dX_+1;		// More comfortable method required. Maybe make center line using x-coordinates of patch points!
	Info << nPoints << endl;

	// Create fields.
	vectorField centerLineOriginal(nPoints,vector(0,0,0));			// Original center line without deformation.
	vectorField centerLineDeformed(nPoints,vector(0,0,0));			// Moving center line.
	vectorField centerLineDisplacement(nPoints,vector(0,0,0));		// Displacement between center line and original center line.
	vectorField centerLineRelativeDisplacement(nPoints,vector(0,0,0));	// Displacement relative to previous point.
	scalarField centerLineRotation(nPoints,0);			// Rotation around previous point.


	// Fill the center line vector field with points.
	forAll (centerLineOriginal,i1)
	{ 
		centerLineOriginal[i1] = vector(i1*dX_,0,0);
		centerLineDeformed[i1] = vector(i1*dX_,0,0);
		centerLineRelativeDisplacement[i1] = vector(i1*dX_,0,0);	// 0 0 0 ?
	};


	// Move each of the center line points in y- and x-direction.	
	forAll (centerLineOriginal,i2)
	{
		// y-displacement
		//centerLine[i2][1] = centerLine[i2][0] * t.value();
		centerLineDeformed[i2][1] = sin( omega_ * t.value() - phi * centerLineDeformed[i2][0]) * (a_ * pow(centerLineDeformed[i2][0], 2) + b_*centerLineDeformed[i2][0] + c_);

		// Calculate displacement between subsequent points and integrate
		// over the center line. Skip for first point which does not displace x-wise.
		if ( i2 != 0 )
		{
			// Calculate y-displacement between subsequent points.
			centerLineRelativeDisplacement[i2][1] = centerLineDeformed[i2][1] - centerLineDeformed[i2-1][1];

			// Calculate x-displacement from y-displacement.
			centerLineRelativeDisplacement[i2][0] = dX_ - sqrt( mag( pow( dX_, 2) - pow( centerLineRelativeDisplacement[i2][1], 2) ));// - dX_;

			// Integrate x-displacement up to the current point.
			deltaXsum += centerLineRelativeDisplacement[i2][0];

			// Move the real center line x-wise.
			centerLineDeformed[i2][0] -= deltaXsum;
		}
	}



// *****************************************************************************
// Calculate the translation and rotation of each point of the center line. ****
// *****************************************************************************

	// Displacement.
	centerLineDisplacement = centerLineDeformed - centerLineOriginal;

	// Rotation.
	forAll(centerLineDeformed, i3)
	{
		// Write the rotation of each point according to the movement of the previous and next point. tan(angle) = deltaY / deltaX
		vector currentPoint = centerLineDeformed[i3];
		vector previousPoint = centerLineDeformed[i3-1];
		vector nextPoint = centerLineDeformed[i3+1];

		scalar currentAngle;
		scalar previousAngle;

		// Calculate current angle except for last point.
		if(i3 != centerLineDeformed.size())
		{
			currentAngle = atan( ( nextPoint[1] - currentPoint[1] ) / ( nextPoint[0] - currentPoint[0] ));
		}
		else
		{
			// Set current angle for last point.
			currentAngle = 0;
		}


		// Calculate previous angle, except for first point.
		if(i3 != 0)
		{
			previousAngle = atan( ( currentPoint[1] - previousPoint[1] ) / ( currentPoint[0] - previousPoint[0] ));

			// Average angle.
			centerLineRotation[i3] = previousAngle - currentAngle;
		}
		else
		{
			// Set previous angle for first point.
			previousAngle = 0;
		}

		// Average angle.
		centerLineRotation[i3] = (previousAngle + currentAngle)/2;
	};


// *****************************************************************************
// Move the patch points according to the center line. *************************
// *****************************************************************************

// Do this for each and every point on the patch.
forAll(pointPatchOriginal,i4)
{
	// Vector for an individual point of the patch.
	vector pointOriginal = pointPatchOriginal[i4];
	vector pointOriginalRel;

	// Vectors for translational and rotational displacement.
	// These will be calculated independently and added afterwards.
	vector translation;
	scalar rotationAngle;
	vector rotation = vector(0,0,0);

	// Displacement vector for combined translation and rotation.
	vector rotationTranslation = vector(0,0,0);

	// Loop through the original center line, determine the points which enclose the current patch point and extract their translation and rotation values.
	forAll(centerLineOriginal, i5)
	{
		// Current point.
		vector centerLinePoint0 = centerLineOriginal[i5];		
		vector centerLinePoint1;

		// The next point. Special treatment for last point.
		if (i5 == centerLineOriginal.size())
		{
			centerLinePoint1 = centerLineOriginal[i5];

		}
		else
		{
			centerLinePoint1 = centerLineOriginal[i5+1];
		}

		// Check if current patch point lies between the current centerline points and does not coincide with a center line point.
		if (   pointOriginal[0] >= centerLinePoint0[0]   &&   pointOriginal[0] < centerLinePoint1[0]   &&   fabs(pointOriginal[0] - centerLinePoint0[0]) > SMALL
			&&   fabs(pointOriginal[0] - centerLinePoint1[0]) > SMALL   )
			{

			// Determine the x-position of the patch point between the two center line points.
			scalar position = (pointOriginal[0] - centerLinePoint0[0]) / dX_;

			// Determine translation slope between center line points.
			vector translationSlope = (centerLineDisplacement[i5+1] - centerLineDisplacement[i5]);

			// Extract the translation from center line points and determine
			// patch point translation by interpolation between the adjacent centerline points.
			//translation = centerLineDisplacement[i5] + (centerLineDisplacement[i5+1] - centerLineDisplacement[i5] ) * position;
			translation = centerLineDisplacement[i5] + translationSlope * position;

			// Determine translation slope between center line points.
			scalar rotationAngleSlope = (centerLineRotation[i5+1] - centerLineRotation[i5]);



			// Extract the rotation angle. Linear interpolation between the adjacent centerline points.
			rotationAngle = centerLineRotation[i5] + rotationAngleSlope * position;

			// Get local coordinates of patch point relative to position between center line points.
			pointOriginalRel = pointOriginal - vector (pointOriginal[0], 0, 0);

			// Rotate the current patch point around the nearest center line point according to its rotation angle. Subtract original point for displacement.
			rotation[0] = (   pointOriginalRel[0] * cos(rotationAngle)   )   -   (   pointOriginalRel[1] * sin(rotationAngle)   )  -  pointOriginalRel[0];
			rotation[1] = (   pointOriginalRel[0] * sin(rotationAngle)   )   +   (   pointOriginalRel[1] * cos(rotationAngle)   )  -  pointOriginalRel[1];
		        	//Info<< "rotation at point " << i5 << " = " << rotation << nl << endl;
			
			rotationTranslation = translation + rotation;

		}
		// Check if current patch point is coinciding with centerline point except for last one.
		else if (   fabs(pointOriginal[0] - centerLinePoint0[0]) <= SMALL   && centerLinePoint0 != centerLinePoint1)
		{

			// Extract the translation.
			translation = centerLineDisplacement[i5];
			
			// Extract the rotation angle.
			rotationAngle = centerLineRotation[i5];

			// Get local coordinates of patch point relative to centerLinePoint.
			pointOriginalRel = pointOriginal - vector (pointOriginal[0], 0, 0);

			// Rotate the current patch point around the nearest center line point according to its rotation angle.
			rotation[0] = (   pointOriginalRel[0] * cos(rotationAngle)   )   -   (   pointOriginalRel[1] * sin(rotationAngle)   )  -  pointOriginalRel[0];
			rotation[1] = (   pointOriginalRel[0] * sin(rotationAngle)   )   +   (   pointOriginalRel[1] * cos(rotationAngle)   )  -  pointOriginalRel[1];

			rotationTranslation = translation + rotation;
		}
		else if (   fabs(pointOriginal[0] - centerLinePoint0[0]) <= SMALL   && centerLinePoint0 == centerLinePoint1)
		{

			translation = centerLineDisplacement[i5];
		        	//Info<< "Loop 2: translation at patch point " << i4 << " " << pointOriginal << ", centerline point " << i5 << " " << centerLinePoint1 << " = " << translation << endl;
				//Info << "	P1 (" << i5 << ") = " << centerLinePoint0 << ", P2 (" << i5+1 << ") = " << centerLinePoint1 << endl;
			Info << "Last CLP met. Trans: " << translation << endl;
			rotationTranslation = translation;// + rotation;
		}

	};


	// The current point displacement is written into the patch. No turning back to the former coordinate system is needed because all we want is the displacement.
	pointPatchDisplacement[i4]=rotationTranslation;
	
};
 

	// Start slowly...
	if (t.value() < 1)	pointPatchDisplacement *= -pow( (t.value()-1), 2) + 1;

	vectorField::operator=
	(
		pointPatchDisplacement
	);

//	fixedValuePointPatchVectorField::updateCoeffs();
	fixedValuePointPatchField<vector>::updateCoeffs(); //For OF-1.7.x instead!!!!!
}


void fishUndulationPointPatchVectorField::write
(
    Ostream& os
) const
{
	// Every value that is read from the pointDisplacement file in the 0 directory has to be written to the next timestep.
    pointPatchField<vector>::write(os);

    os.writeKeyword("origin")	<< origin_ << token::END_STATEMENT << nl;
    os.writeKeyword("dX")	<< dX_ << token::END_STATEMENT << nl;
    os.writeKeyword("omega")	<< omega_ << token::END_STATEMENT << nl;
    os.writeKeyword("length")	<< length_ << token::END_STATEMENT << nl;
    os.writeKeyword("waveLength")	<< waveLength_ << token::END_STATEMENT << nl;
    os.writeKeyword("a")	<< a_ << token::END_STATEMENT << nl;
    os.writeKeyword("b")	<< b_ << token::END_STATEMENT << nl;
    os.writeKeyword("c")	<< c_ << token::END_STATEMENT << nl;

    // Write the displacement values
    writeEntry("value", os);
}


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

makePointPatchTypeField
(
    pointPatchVectorField,
    fishUndulationPointPatchVectorField
);

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// ************************************************************************* //
