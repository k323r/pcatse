/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | Copyright (C) 2011-2013 OpenFOAM Foundation
     \\/     M anipulation  |
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
    Foam::power

Group
    grpForcesFunctionObjects

Description
    This function object calculates the power which is necessary to move a wall 
    in a fluid by integrating the inner product of surface forces (pressure and 
    skin-friction forces) and the velocity of the moving wall over a given list 
    of patches.

    Member function power::write() calculates the power and
    writes the power into the file \<timeDir\>/power.dat

    Example of function object specification:
    \verbatim
    power1
    {
        type        power;
        functionObjectLibs ("libpower.so");
        ...
        log         yes;
        patches     (walls);
    }
    \endverbatim

    \heading Function object usage
    \table
        Property     | Description             | Required    | Default value
        type         | type name: power       | yes         |
        log          | write power data to standard output | no | no
        patches      | patches included in the power calculation | yes |
        pName        | pressure field name     | no          | p
        UName        | velocity field name     | no          | U
        rhoName      | density field name (see below) | no   | rho
    \endtable

Note
  - For incompressible cases, set \c rhoName to \c rhoInf.  You will then be
    required to provide a \c rhoInf value corresponding to the free-stream
    constant density.

SeeAlso
    Foam::functionObject
    Foam::OutputFilterFunctionObject
    Foam::powerCoeffs

SourceFiles
    power.C
    IOpower.H

\*---------------------------------------------------------------------------*/

#ifndef power_H
#define power_H

#include "functionObjectFile.H"
#include "coordinateSystem.H"
#include "coordinateSystems.H"
#include "primitiveFieldsFwd.H"
#include "volFieldsFwd.H"
#include "HashSet.H"
#include "Tuple2.H"
#include "OFstream.H"
#include "Switch.H"
#include "writer.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

// Forward declaration of classes
class objectRegistry;
class dictionary;
class polyMesh;
class mapPolyMesh;

/*---------------------------------------------------------------------------*\
                           Class power Declaration
\*---------------------------------------------------------------------------*/

class power
:
    public functionObjectFile
{
protected:

    // Protected data

        //- Name of this set of power,
        //  Also used as the name of the probes directory.
        word name_;

        const objectRegistry& obr_;

        //- On/off switch
        bool active_;

        //- Switch to send output to Info as well as to file
        Switch log_;

        //- Pressure, viscous and porous power per bin
        List<Field<vector> > power_;

        // Read from dictionary

            //- Patches to integrate power over
            labelHashSet patchSet_;

            //- Name of pressure field
            word pName_;

            //- Name of velocity field
            word UName_;

            //- Name of density field (optional)
            word rhoName_;

            //- Is the power density being supplied directly?
            Switch directForceDensity_;

            //- The name of the power density (fD) field
            word fDName_;

            //- Reference density needed for incompressible calculations
            scalar rhoRef_;

            //- Reference pressure
            scalar pRef_;

            //- Flag to indicate whether we are using a local co-ordinate sys
            bool localSystem_;

            //- Flag to include porosity effects
            bool porosity_;


            // Bin information

                //- Number of bins
                label nBin_;


    // Protected Member Functions

        //- Output file header information
        virtual void writeFileHeader(const label i);

        //- Return the effective viscous stress (laminar + turbulent).
        tmp<volSymmTensorField> devRhoReff() const;

        //- Dynamic viscosity field
        tmp<volScalarField> mu() const;

        //- Return rho if rhoName is specified otherwise rhoRef
        tmp<volScalarField> rho() const;

        //- Return rhoRef if the pressure field is dynamic, i.e. p/rho
        //  otherwise return 1
        scalar rho(const volScalarField& p) const;

        //- Accumulate bin data
        void applyBins
        (
            const vectorField& Power
        );

        //- Helper function to write bin data
        void writeBins() const;

        //- Disallow default bitwise copy construct
        power(const power&);

        //- Disallow default bitwise assignment
        void operator=(const power&);


public:

    //- Runtime type information
    TypeName("power");


    // Constructors

        //- Construct for given objectRegistry and dictionary.
        //  Allow the possibility to load fields from files
        power
        (
            const word& name,
            const objectRegistry&,
            const dictionary&,
            const bool loadFromFiles = false
        );


        //- Construct from components
        power
        (
            const word& name,
            const objectRegistry&,
            const labelHashSet& patchSet,
            const word& pName,
            const word& UName,
            const word& rhoName,
            const scalar rhoInf,
            const scalar pRef
        );


    //- Destructor
    virtual ~power();


    // Member Functions

        //- Return name of the set of power
        virtual const word& name() const
        {
            return name_;
        }

        //- Read the power data
        virtual void read(const dictionary&);

        //- Execute, currently does nothing
        virtual void execute();

        //- Execute at the final time-loop, currently does nothing
        virtual void end();

        //- Called when time was set at the end of the Time::operator++
        virtual void timeSet();

        //- Write the power
        virtual void write();

        //- Calculate the power and moments
        virtual void calcPower();

        //- Return the total power
        virtual vector powerEff() const;

        //- Update for changes of mesh
        virtual void updateMesh(const mapPolyMesh&)
        {}

        //- Update for changes of mesh
        virtual void movePoints(const polyMesh&)
        {}
};


// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
