#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""rna_pdb_toolsx - a swiss army knife to manipulation of RNA pdb structures

Tricks:

   for i in *pdb; do rna_pdb_toolsx.py --get_rnapuzzle_ready $i >  ${i/.pdb/_rpr.pdb}; done

Usage::

   $ for i in *pdb; do rna_pdb_toolsx.py --delete A:46-56 $i > ../rpr_rm_loop/$i ; done

    $ rna_pdb_toolsx.py --get_seq *
    # BujnickiLab_RNApuzzle14_n01bound
    > A:1-61
    # BujnickiLab_RNApuzzle14_n02bound
    > A:1-61
    CGUUAGCCCAGGAAACUGGGCGGAAGUAAGGCCCAUUGCACUCCGGGCCUGAAGCAACGCG
    [...]

"""
from __future__ import print_function

import argparse
import os
import progressbar
import tempfile

from rna_tools_lib import *
from rna_tools.tools.rna_x3dna.rna_x3dna import x3DNA


def get_parser():
    version = os.path.basename(os.path.dirname(os.path.abspath(__file__))), get_version(__file__)
    version = version[1].strip()
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--version', help='', action='version', version=version)

    parser.add_argument('-r', '--report', help='get report',
                        action='store_true')

    parser.add_argument('--delete-anisou', help='remove files with ANISOU records, works with --inplace',
                        action='store_true')

    parser.add_argument('--split-alt-locations', help='@todo',
                        action='store_true')

    parser.add_argument('-c', '--clean', help='get clean structure',
                        action='store_true')

    parser.add_argument('--is_pdb', help='check if a file is in the pdb format',
                        action='store_true')

    parser.add_argument('--is_nmr', help='check if a file is NMR-style multiple model pdb',
                        action='store_true')

    parser.add_argument('--un_nmr', help='Split NMR-style multiple model pdb files into individual models [biopython]',
                        action='store_true')

    parser.add_argument('--orgmode', help='get a structure in org-mode format <sick!>',
                        action='store_true')

    parser.add_argument('--get_chain', help='get chain, .e.g A')

    parser.add_argument('--fetch', action='store_true', help='fetch file from the PDB db')

    parser.add_argument('--fetch_ba', action='store_true',
                        help='fetch biological assembly from the PDB db')

    parser.add_argument('--get_seq', help='get seq', action='store_true')
    parser.add_argument('--compact', help='with --get_seq, get it in compact view' , action='store_true')

    parser.add_argument('--get_ss', help='get secondary structure', action='store_true')

    parser.add_argument('--rosetta2generic', help='convert ROSETTA-like format to a generic pdb',
                        action='store_true')

    parser.add_argument('--get_rnapuzzle_ready', help='get RNApuzzle ready (keep only standard atoms).'
                                                      'Be default it does not renumber residues, use --renumber_residues '
                                                      '[requires biopython]', action='store_true')

    parser.add_argument('--rpr', help='alias to get_rnapuzzle ready)',
                        action='store_true')

    parser.add_argument('--no_hr', help='do not insert the header into files',
                        action='store_true')

    parser.add_argument('--renumber_residues', help='by defult is false',
                        action='store_true')

    parser.add_argument('--dont_rename_chains', help="""used only with --get_rnapuzzle_ready. By default \
                                                      --get_rnapuzzle_ready rename chains from ABC.. to stop behavior switch on this option""",
                        action='store_true')

    parser.add_argument('--dont_fix_missing_atoms',
                        help="""used only with --get_rnapuzzle_ready""",
                        action='store_true')

    parser.add_argument('--dont_report_missing_atoms',
                        help="""used only with --get_rnapuzzle_ready""",
                        action='store_true')

    parser.add_argument('--collapsed_view', help='',
                        action='store_true')

    parser.add_argument('--cv', help='alias to collapsed_view',
                        action='store_true')

    parser.add_argument('-v', '--verbose', help='tell me more what you\'re doing, please!',
                        action='store_true')

    parser.add_argument('--replace_hetatm', help="replace 'HETATM' with 'ATOM' [tested only with --get_rnapuzzle_ready]",
                        action="store_true")

    parser.add_argument('--inplace', help='in place edit the file! [experimental, only for get_rnapuzzle_ready, delete, get_ss, get_seq]',
                        action='store_true')

    parser.add_argument('--mutate', help="""mutate residues, e.g. A:1A+2A+3A+4A,B:1A to mutate the first nucleotide of the A chain to Adenine etc and the first nucleotide of the B chain""")

    parser.add_argument('--edit',
                        dest="edit",
                        default='',
                        help="edit 'A:6>B:200', 'A:2-7>B:2-7'")

    parser.add_argument('--rename-chain',
                        help="edit 'A>B' to rename chain A to chain B")

    parser.add_argument('--replace-chain',
                        default='',
                        help="a file PDB name with one chain that will be used to replace the chain in the original PDB file, the chain id in this file has to be the same with the chain id of the original chain")

    parser.add_argument('--delete',  # type="string",
                        dest="delete",
                        default='',
                        help="delete the selected fragment, e.g. A:10-16, or for more than one fragment --delete 'A:1-25+30-57'")

    parser.add_argument('--extract',  # type="string",
                        dest="extract",
                        default='',
                        help="extract the selected fragment, e.g. A:10-16, or for more than one fragment --extract 'A:1-25+30-57'")

    parser.add_argument('--uniq', help="")
    parser.add_argument('--chain-first', help="")

    parser.add_argument('file', help='file', nargs='+')
    #parser.add_argument('outfile', help='outfile')
    return parser


# main
if __name__ == '__main__':
    # get version
    version = os.path.basename(os.path.dirname(os.path.abspath(__file__))), get_version(__file__)
    version = version[1].strip()

    # get parser and arguments
    parser = get_parser()

    args = parser.parse_args()

    # quick fix for one files vs file-s
    if list == type(args.file) and len(args.file) == 1:
        args.file = args.file[0]

    if args.report:
        s = RNAStructure(args.file)
        print(s.get_report)
        print(s.get_preview())
        print(s.get_info_chains())

    if args.clean:
        s = RNAStructure(args.file)
        s.decap_gtp()
        s.std_resn()
        s.remove_hydrogen()
        s.remove_ion()
        s.remove_water()
        s.renum_atoms()
        s.fix_O_in_UC()
        s.fix_op_atoms()
        # print s.get_preview()
        # s.write(args.outfile)
        if not args.no_hr:
            print(add_header(version))
        print(s.get_text())

    if args.get_seq:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        analyzed = []
        for f in args.file:
            #####################################
            if args.uniq:
                subname = eval('f' + args.uniq)
                if subname in analyzed:
                    continue
                else:
                    analyzed.append(subname)
            ########
            s = RNAStructure(f)
            if not s.is_pdb():
                print('Not a PDF file %s' % f)
            s.decap_gtp()
            s.std_resn()
            s.remove_hydrogen()
            s.remove_ion()
            s.remove_water()
            s.renum_atoms()
            s.fix_O_in_UC()
            s.fix_op_atoms()

            output = ''
            # with # is easier to grep this out
            output += '# ' + os.path.basename(f.replace('.pdb', '')) + '\n'
            output += s.get_seq(compact=args.compact, chainfirst=args.chain_first) + '\n'
            try:
                sys.stdout.write(output)
                sys.stdout.flush()
            except IOError:
                pass

    if args.get_ss:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            output = f + '\n'
            p = x3DNA(f)
            output += p.get_secstruc() + '\n'
            try:
                sys.stdout.write(output)
                sys.stdout.flush()
            except IOError:
                pass

    if args.get_chain:
        s = RNAStructure(args.file)
        s.std_resn()
        s.remove_hydrogen()
        s.remove_ion()
        s.remove_water()
        s.renum_atoms()
        s.fix_O_in_UC()
        s.fix_op_atoms()
        # print s.get_preview()
        print(s.get_chain(args.get_chain))

    if args.rosetta2generic:
        s = RNAStructure(args.file)
        s.std_resn()
        s.remove_hydrogen()
        s.remove_ion()
        s.remove_water()
        s.fix_op_atoms()
        s.renum_atoms()
        # print s.get_preview()
        # s.write(args.outfile)
        if not args.no_hr:
            print(add_header(version))
        print(s.get_text())

    if args.get_rnapuzzle_ready or args.rpr:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################

        # progress bar only in --inplace mode!
        if args.inplace:
            bar = progressbar.ProgressBar(max_value=len(args.file))
            bar.update(0)

        for c, f in enumerate(args.file):
            if args.inplace:
                shutil.copy(f, f + '~')

            # keep previous edits
            previous_edits = []
            with open(f) as fx:
                for l in fx:
                    if l.startswith('HEADER --'):
                        previous_edits.append(l.strip())
            ######################

            s = RNAStructure(f)
            if args.replace_hetatm:
                s.replace_hetatm()
            s.decap_gtp()
            s.std_resn()
            s.remove_hydrogen()
            s.remove_ion()
            s.remove_water()
            s.fix_op_atoms()
            s.renum_atoms()
            s.shift_atom_names()
            s.prune_elements()

            rename_chains = False if args.dont_rename_chains else True

            report_missing_atoms = not args.dont_report_missing_atoms
            fix_missing_atom = not args.dont_fix_missing_atoms

            remarks = s.get_rnapuzzle_ready(args.renumber_residues, fix_missing_atoms=fix_missing_atom,
                                            rename_chains=rename_chains,
                                            report_missing_atoms=report_missing_atoms,
                                            verbose=args.verbose)

            if args.inplace:
                with open(f, 'w') as f:
                    if not args.no_hr:
                        f.write(add_header(version) + '\n')
                    if previous_edits:
                        f.write('\n'.join(previous_edits) + '\n')
                    if remarks:
                        f.write('\n'.join(remarks) + '\n')
                    f.write(s.get_text())

                # progress bar only in --inplace mode!
                bar.update(c)

            else:
                output = ''
                if not args.no_hr:
                    output += add_header(version) + '\n'
                if remarks:
                    output += '\n'.join(remarks) + '\n'
                output += s.get_text() + '\n'
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass
        # hmm... fix for problem with renumbering, i do renumbering
        # and i stop here
        # i'm not sure that this is perfect
        sys.exit(0)

    if args.renumber_residues:
        s = RNAStructure(args.file)
        s.remove_hydrogen()
        s.remove_ion()
        s.remove_water()
        s.get_rnapuzzle_ready(args.renumber_residues)
        s.renum_atoms()
        if not args.no_hr:
            print(add_header(version))
        print(s.get_text())

    if args.delete:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')

            selection = select_pdb_fragment(args.delete)
            s = RNAStructure(f)

            output = ''
            if not args.no_hr:
                output += add_header(version) + '\n'
                output += 'HEADER --delete ' + args.delete + '\n'  # ' '.join(str(selection))
            for l in s.lines:
                if l.startswith('ATOM'):
                    chain = l[21]
                    resi = int(l[23:26].strip())
                    if chain in selection:
                        if resi in selection[chain]:
                            continue  # print chain, resi
                    output += l + '\n'

            # write: inplace
            if args.inplace:
                with open(f, 'w') as f:
                    f.write(output)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass

    if args.replace_chain:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')

            # --replace_chain <file> without A:<file> it will be easier than --x "A:<file>"
            s = RNAStructure(args.replace_chain)
            chain_ids = (s.get_all_chain_ids())
            if len(chain_ids) > 1:
                raise Exception('There is more than one chain in the inserted PDB file. There should be only one chain, the one you want to insert to the PDB.')
            out = replace_chain(f, args.replace_chain, list(chain_ids)[0])
            print(out)

    if args.mutate:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        try:
            from moderna import *
        except ImportError:
            raise Exception('To use this functionality please install ModeRNA, e.g. pip install moderna')

        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')  # create a backup copy if inplace

            # create a working copy of the main file
            ftf = tempfile.NamedTemporaryFile(delete=False).name  # f temp file
            shutil.copy(f, ftf)  # create a backup copy if inplace

            # go over each chain
            for m in args.mutate.split(','):  # A:1A, B:1A
                chain, resi_mutate_to = m.strip().split(':')  # A:1A+2C
                resi_mutate_to_list = resi_mutate_to.split('+')  # A:1A+2C

                model = load_model(f, chain)
                # go over each mutation in this chain
                for resi_mutate_to in resi_mutate_to_list:
                    resi = resi_mutate_to[:-1]
                    mutate_to = resi_mutate_to[-1]
                    if args.verbose:
                        print('Mutate', model[resi], 'to', mutate_to)
                    exchange_single_base(model[resi], mutate_to)

                # multi mutation in one chain
                tf = tempfile.NamedTemporaryFile(delete=False)
                model.write_pdb_file(tf.name)

                # work on the copy of f, ftf
                output = replace_chain(ftf, tf.name, chain)
                with open(ftf, 'w') as tmp:
                    tmp.write(output)

            # write: inplace
            if args.inplace:
                # ftf now is f, get ready for the final output
                shutil.copy(ftf, f)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass


    if args.extract:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')

            selection = select_pdb_fragment(args.extract)
            s = RNAStructure(f)

            output = ''
            if not args.no_hr:
                output += add_header(version) + '\n'
                output += 'HEADER extract ' + args.extract + '\n'  # ' '.join(str(selection))
            for l in s.lines:
                if l.startswith('ATOM'):
                    chain = l[21]
                    resi = int(l[23:26].strip())
                    if chain in selection:
                        if resi in selection[chain]:
                            # continue  # print chain, resi
                            output += l + '\n'

            # write: inplace
            if args.inplace:
                with open(f, 'w') as f:
                    f.write(output)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass


    if args.un_nmr:
        pass

    if args.is_pdb:
        s = RNAStructure(args.file)
        output = str(s.is_pdb())
        sys.stdout.write(output + '\n')

    if args.un_nmr:
        s = RNAStructure(args.file)
        str(s.un_nmr())

    if args.is_nmr:
        s = RNAStructure(args.file)
        output = str(s.is_nmr(args.verbose))
        sys.stdout.write(output + '\n')

    if args.edit:
        edit_pdb(args)

    if args.fetch:
        fetch(args.file)

    if args.fetch_ba:
        fetch_ba(args.file)

    if args.collapsed_view or args.cv:
        collapsed_view(args)

    if args.delete_anisou:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')

            s = RNAStructure(f)

            output = ''
            if not args.no_hr:
                output += add_header(version) + '\n'

            for l in s.lines:
                if l.startswith('ANISOU'):
                    continue
                else:
                    output += l + '\n'

            if args.inplace:
                with open(f, 'w') as f:
                    f.write(output)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass


    if args.rename_chain:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')
            # rename_chain 'A>B'
            s = RNAStructure(f)
            chain_id_old, chain_id_new = args.rename_chain.split('>')
            output = ''
            if not args.no_hr:
                output += add_header(version) + '\n'
            output += s.rename_chain(chain_id_old, chain_id_new)
            if args.inplace:
                with open(f, 'w') as f:
                    f.write(output)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass


    if args.split_alt_locations:
        # quick fix - make a list on the spot
        if list != type(args.file):
            args.file = [args.file]
        ##################################
        for f in args.file:
            if args.inplace:
                shutil.copy(f, f + '~')

            #s = RNAStructure(f)
            s = open(f)
            output = ''
            if not args.no_hr:
                output += add_header(version) + '\n'

            # First, collect all alternative locations.
            alts = set()
            for l in s:
                if l.startswith('ATOM'):
                    if l[16].strip():
                        alts.add(l[16])
            s.close()

            if args.verbose:
                print('alts:', alts)

            for index, alt in enumerate(alts):
                output += 'MODEL %i' % (index + 1)
                s = open(f)
                for l in s:
                    if l.startswith('ATOM') or l.startswith('HETATM'):
                        # if empty, then print this line
                        if l[16] == ' ':
                            output += l
                        if l[16] == alt:
                            output += l
                    else:
                        output += l
                output += 'ENDMDL\n'
                s.close()

            if args.inplace:
                with open(f, 'w') as f:
                    f.write(output)
            else:  # write: to stdout
                try:
                    sys.stdout.write(output)
                    sys.stdout.flush()
                except IOError:
                    pass

    if args.orgmode:
        if args.inplace:
            shutil.copy(args.file, args.file + '~')
        s = RNAStructure(args.file)
        s.decap_gtp()
        s.std_resn()
        s.remove_hydrogen()
        s.remove_ion()
        s.remove_water()
        s.fix_op_atoms()
        s.renum_atoms()
        s.shift_atom_names()
        s.prune_elements()
        # print s.get_preview()
        # s.write(args.outfile)
        # for l in s.lines:
        #    print l

        remarks = s.get_rnapuzzle_ready(
            args.renumber_residues, fix_missing_atoms=True, rename_chains=True, verbose=args.verbose)

        with open(args.file + '~', 'w') as f:
            if not args.no_hr:
                f.write(add_header(version) + '\n')

            f.write('\n'.join(remarks) + '\n')
            f.write(s.get_text())

        try:
            from Bio import PDB
            from Bio.PDB import PDBIO
            import warnings
            warnings.filterwarnings('ignore', '.*Invalid or missing.*',)
            warnings.filterwarnings('ignore', '.*with given element *',)
        except:
            sys.exit('Error: Install biopython to use this function (pip biopython)')

        parser = PDB.PDBParser()
        struct = parser.get_structure('', args.file + '~')
        model = struct[0]

        # chains [['A', 'seq', [residues]]]
        chains = []
        for c in model.get_list():
            seq = ''
            chain = []
            for r in c:
                chain.append(str(r.get_resname().strip()) + str(r.id[1]))
                seq += r.get_resname().strip()
            chains.append([c.id, seq, chain])

        t = []
        #[['A', 'CCGCCGCGCCAUGCCUGUGGCGG', ['C1', 'C2', 'G3', 'C4', 'C5', 'G6', 'C7', 'G8', 'C9', 'C10', 'A11', 'U12', 'G13', 'C14', 'C15', 'U16', 'G17', 'U18', 'G19', 'G20', 'C21', 'G22', 'G23']], ['B', 'CCGCCGCGCCAUGCCUGUGGCGG', ['C1', 'C2', 'G3', 'C4', 'C5', 'G6', 'C7', 'G8', 'C9', 'C10', 'A11', 'U12', 'G13', 'C14', 'C15', 'U16', 'G17', 'U18', 'G19', 'G20', 'C21', 'G22', 'G23']]]
        for c in chains:
            t.append('* ' + c[0] + ':' + c[2][0][1:] + '-' + c[2][-1][1:] + ' ' + c[1])
            for r in c[2]:
                t.append('** ' + c[0] + ':' + r)
        print('\n'.join(t))
