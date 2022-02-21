/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2012-2016 OpenFOAM Foundation
    Copyright (C) 2019-2020 OpenCFD Ltd.
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

Class
    Foam::functionObjects::grad

Group
    grpFieldFunctionObjects

Description
    Computes the gradient of an input field.

    The operation is limited to scalar and vector volume or surface fields, and
    the output is a volume vector or tensor field.

    Operands:
    \table
      Operand       | Type                              | Location
      input         | {vol,surface}{Scalar,Vector}Field <!--
                --> | $FOAM_CASE/\<time\>/\<inpField\>
      output file   | -                                 | -
      output field  | vol{Vector,Tensor}Field           <!--
                --> | $FOAM_CASE/\<time\>/\<outField\>
    \endtable

Usage
    Minimal example by using \c system/controlDict.functions:
    \verbatim
    targetSize1
    {
        // Mandatory entries (unmodifiable)
        type            targetSize;
        libs            (fieldFunctionObjects);

        // Mandatory (inherited) entries (runtime modifiable)
        field           <field>;

        // Optional (inherited) entries
        ...
    }
    \endverbatim

    where the entries mean:
    \table
      Property     | Description                        | Type | Req'd | Dflt
      type         | Type name: targetSize                    | word |  yes  | -
      libs         | Library name: fieldFunctionObjects | word |  yes  | -
      field        | Name of the operand field          | word |  yes  | -
    \endtable

    The inherited entries are elaborated in:
     - \link functionObject.H \endlink
     - \link fieldExpression.H \endlink

    Minimal example by using the \c postProcess utility:
    \verbatim
        postProcess -func "targetSize(<field>)"
    \endverbatim

See also
    - Foam::functionObject
    - Foam::functionObjects::fvMeshFunctionObject
    - Foam::functionObjects::fieldExpression
    - ExtendedCodeGuide::functionObjects::field::targetSize

SourceFiles
    targetSize.C
    targetSizeTemplates.C

\*---------------------------------------------------------------------------*/

#ifndef functionObjects_targetSize_H
#define functionObjects_targetSize_H

#include "fieldExpression.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{
namespace functionObjects
{

/*---------------------------------------------------------------------------*\
                         Class targetSize Declaration
\*---------------------------------------------------------------------------*/

class targetSize
:
    public fieldExpression
{
    // Private Member Functions

        //- Calculate the magnitude of the field and register the result
        template<class Type>
        bool calctargetSize();

        //- Calculate the targetSizeField field and return true if successful
        virtual bool calc();

        //- Get or initialize the targetSizeField
        volScalarField& getOrInitializeSizeField();


public:

    //- Runtime type information
    TypeName("targetSize");


    // Constructors

        //- Construct from Time and dictionary
        targetSize
        (
            const word& name,
            const Time& runTime,
            const dictionary& dict
        );

        //- No copy construct
        targetSize(const targetSize&) = delete;

        //- No copy assignment
        void operator=(const targetSize&) = delete;


    //- Destructor
    virtual ~targetSize() = default;
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace functionObjects
} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#ifdef NoRepository
    #include "targetSizeTemplates.C"
#endif

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
