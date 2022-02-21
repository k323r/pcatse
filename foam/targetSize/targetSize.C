/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2013-2016 OpenFOAM Foundation
    Copyright (C) 2019 OpenCFD Ltd.
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

\*---------------------------------------------------------------------------*/

#include "targetSize.H"
#include "addToRunTimeSelectionTable.H"
#include "fvcGrad.H"
#include "fvCFD.H"
#include "volFields.H"

// * * * * * * * * * * * * * * Static Data Members * * * * * * * * * * * * * //

namespace Foam
{
namespace functionObjects
{
    defineTypeNameAndDebug(targetSize, 0);
    addToRunTimeSelectionTable(functionObject, targetSize, dictionary);
}
}


// * * * * * * * * * * * * * Private Member Functions  * * * * * * * * * * * //
Foam::volScalarField& Foam::functionObjects::targetSize::getOrInitializeSizeField()
{
    if (!foundObject<volScalarField>(resultName_))
    {
        auto tfldPtr = tmp<volScalarField>::New
        (
            IOobject
            (
                resultName_,
                mesh_.time().timeName(),
                mesh_,
                IOobject::MUST_READ,
                IOobject::AUTO_WRITE
            ),
            mesh_
        );
        store(resultName_, tfldPtr);
    }

    return lookupObjectRef<volScalarField>(resultName_);
}


bool Foam::functionObjects::targetSize::calc()
{
    //bool processed = false;

    //processed = processed || calctargetSize<scalar>();
    //processed = processed || calctargetSize<vector>();


    // This has to be changed to be adaptable to scalar and vector field
    //volScalarField St = 
    //Foam::tmp<volScalarField>::New


    volScalarField& St = getOrInitializeSizeField();

    volTensorField uGrad = fvc::grad(lookupObject<volVectorField>(fieldName_));

    vector dist;

    // Iterate over all mesh cell labels
    forAll(mesh_.C(), cellI)
    {
        // For current cell, get List of neighbourCells
        const Foam::labelList& neighBourCellLabels(mesh_.cellCells()[cellI]);

        // Iterate over all 
        forAll(neighBourCellLabels, neighbourI)
        {
            // Get (absolute) label/index of neighbour cell
            label curNeighbour = mesh_.cellCells()[cellI][neighbourI];
            dist = mesh_.C()[curNeighbour] - mesh_.C()[cellI];
            vector h_hat_j = dist / mag(dist);
            vector grad_at_C = h_hat_j & uGrad[cellI];
            vector grad_at_F = h_hat_j & uGrad[curNeighbour];
            St[cellI] = mag(grad_at_C - grad_at_F);
            //St[cellI] = Foam::mag((h_hat_j & uGrad[cellI]) - Foam::mag(h_hat_j & uGrad[curNeighbour]);
            //auto sensor_value =  fvc::grad(lookupObject<volVectorField>(fieldName_))[curNeighbour] - fvc::grad(lookupObject<volVectorField>(fieldName_))[cellI]));
        }
    }
/*
    const bool isNew = false;

    if (isNew)
    {
	    volScalarField St
	    (
		IOobject
		(
			resultName_,
			mesh_.time().timeName(),
			mesh_,
			IOobject::MUST_READ,
			IOobject::AUTO_WRITE
		),
	    mesh_
	    );

	    // value
	    Info << "Ran targetSize::calc() successfully" << endl;
    }
    
    //St = Foam::mag(fvc::grad(lookupObject<volVectorField>(fieldName_)));
    //store(resultName_, St);
    */
    //return store(resultName_, St);
    return true;
}


// * * * * * * * * * * * * * * * * Constructors  * * * * * * * * * * * * * * //

Foam::functionObjects::targetSize::targetSize
(
    const word& name,
    const Time& runTime,
    const dictionary& dict
)
:
    fieldExpression(name, runTime, dict)
{
    volScalarField& St = getOrInitializeSizeField();
}


// ************************************************************************* //
