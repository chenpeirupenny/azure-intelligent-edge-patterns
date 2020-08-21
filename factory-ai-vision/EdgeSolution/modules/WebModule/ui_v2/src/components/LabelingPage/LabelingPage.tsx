import React, { FC, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { createSelector } from '@reduxjs/toolkit';
import { Dialog, Button, DialogFooter, Stack, TextField, DetailsList } from '@fluentui/react';

import { State } from 'RootStateType';
import { LabelingType, WorkState } from './type';
import { closeLabelingPage, goPrevImage, goNextImage } from '../../store/labelingPageSlice';
import { selectImageEntities, saveLabelImageAnnotation } from '../../store/imageSlice';
import { labelPageAnnoSelector } from '../../store/annotationSlice';
import { Annotation } from '../../store/type';
import { selectPartEntities, Part } from '../../store/partSlice';
import { deleteImage } from '../../store/actions';
import Scene from './Scene';
import { PartPicker } from './PartPicker';

const getSelectedImageId = (state: State) => state.labelingPage.selectedImageId;
export const imageSelector = createSelector(
  [getSelectedImageId, selectImageEntities],
  (selectedImageId, imageEntities) => imageEntities[selectedImageId],
);
const imagePartSelector = createSelector([imageSelector, selectPartEntities], (img, partEntities) => {
  if (img) return partEntities[img.part];
  return { id: null, name: '', description: '' };
});

interface LabelingPageProps {
  labelingType: LabelingType;
  isRelabel: boolean;
}

const LabelingPage: FC<LabelingPageProps> = ({ labelingType, isRelabel }) => {
  const dispatch = useDispatch();
  const imageIds = useSelector<State, number[]>((state) => state.labelingPage.imageIds);
  const selectedImageId = useSelector<State, number>((state) => state.labelingPage.selectedImageId);
  const index = imageIds.findIndex((e) => e === selectedImageId);
  const imageUrl = useSelector<State, string>((state) => imageSelector(state)?.image || '');
  const imgPart = useSelector<State, Part>(imagePartSelector);
  const closeDialog = () => dispatch(closeLabelingPage());
  const [workState, setWorkState] = useState<WorkState>(WorkState.None);
  const [loading, setLoading] = useState(false);

  const annotations = useSelector<State, Annotation[]>(labelPageAnnoSelector);

  const isOnePointBox = checkOnePointBox(annotations);

  const onSave = async (isRelabelDone: boolean) => {
    setLoading(true);
    await dispatch(saveLabelImageAnnotation({ isRelabel, isRelabelDone }));
    setLoading(false);
  };

  const onSaveBtnClick = async () => {
    await onSave(false);
    dispatch(goNextImage());
    if (index === imageIds.length - 1) closeDialog();
  };

  const onDoneBtnClick = (): void => {
    // eslint-disable-next-line no-restricted-globals
    const isRelabelDone = confirm('The Rest of the image will be removed');
    onSave(isRelabelDone);
    if (isRelabelDone) closeDialog();
  };

  const onBoxCreated = (): void => {
    if (index === imageIds.length - 1) onSaveBtnClick();
  };

  const onDeleteImage = async () => {
    setLoading(true);
    await dispatch(deleteImage(selectedImageId));
    setLoading(false);
  };

  return (
    <Dialog
      dialogContentProps={{
        title: 'Image Detail',
        subText: 'Drag a box around object to tag a part',
        styles: { content: { width: '1080px' } },
      }}
      hidden={false}
      onDismiss={closeDialog}
      modalProps={{ isBlocking: true }}
      // Remove the default max-width
      maxWidth={9999}
    >
      <Stack horizontal tokens={{ childrenGap: '10px' }}>
        <div style={{ width: '70%' }}>
          <Scene
            url={imageUrl}
            annotations={annotations}
            workState={workState}
            setWorkState={setWorkState}
            labelingType={labelingType}
            onBoxCreated={onBoxCreated}
            partFormDisabled={!isRelabel}
            imgPart={imgPart}
          />
        </div>
        <div style={{ width: '30%' }}>
          <TextField label="Part" placeholder="Add a part" />
          <PartPicker />
        </div>
      </Stack>
      <DialogFooter>
        <Button
          primary
          text={index === imageIds.length - 1 ? 'Save and Done' : 'Save and Next'}
          disabled={isOnePointBox || workState === WorkState.Creating || loading}
          onClick={onSaveBtnClick}
        />
        <Button text="Delete Image" onClick={onDeleteImage} disabled={loading} />
        {isRelabel ? (
          <Button text="Done" onClick={onDoneBtnClick} disabled={loading} />
        ) : (
          <Button
            text="Close"
            onClick={(): void => {
              closeDialog();
            }}
            disabled={loading}
          />
        )}
      </DialogFooter>
    </Dialog>
  );
};

const checkOnePointBox = (annotations: Annotation[]): boolean => {
  if (annotations.length === 0) return false;
  const { label } = annotations[annotations.length - 1];
  return label.x1 === label.x2 && label.y1 === label.y2;
};

export default LabelingPage;